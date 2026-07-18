const API_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')
const ACCESS_TOKEN_KEY = 'railway-access-token'
const REFRESH_TOKEN_KEY = 'railway-refresh-token'
const EXPIRES_AT_KEY = 'railway-token-expires-at'

function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function hasSession() {
  return Boolean(getAccessToken() || getRefreshToken())
}

export function saveSession(session) {
  localStorage.setItem(ACCESS_TOKEN_KEY, session.accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, session.refreshToken)

  const expiresIn = Number(session.expiresIn) || 900000
  localStorage.setItem(EXPIRES_AT_KEY, String(Date.now() + expiresIn))
}

export function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(EXPIRES_AT_KEY)
}

async function parseError(response) {
  let message = `Ошибка запроса: ${response.status}`

  try {
    const data = await response.json()
    message = data.message || data.error || data.detail || data.title || message

    if (data.errors && typeof data.errors === 'object') {
      const validationMessage = Object.values(data.errors).flat().join('. ')
      if (validationMessage) message = validationMessage
    }
  } catch {
    try {
      const text = await response.text()
      if (text) message = text
    } catch {
      // Оставляем стандартное сообщение.
    }
  }

  const error = new Error(message)
  error.status = response.status
  throw error
}

async function refreshSession() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) throw new Error('Сессия истекла. Войдите снова.')

  const response = await fetch(`${API_URL}/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken }),
  })

  if (!response.ok) {
    clearSession()
    await parseError(response)
  }

  const session = await response.json()
  saveSession(session)
  return session
}

async function apiRequest(path, options = {}, retryAfterRefresh = true) {
  const { auth = true, responseType = 'json', headers: customHeaders, ...fetchOptions } = options
  const headers = new Headers(customHeaders || {})
  const bodyIsFormData = fetchOptions.body instanceof FormData

  if (fetchOptions.body && !bodyIsFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (auth) {
    const token = getAccessToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    headers,
  })

  if (response.status === 401 && auth && retryAfterRefresh && getRefreshToken()) {
    try {
      await refreshSession()
      return apiRequest(path, options, false)
    } catch (error) {
      clearSession()
      window.dispatchEvent(new Event('railway:unauthorized'))
      throw error
    }
  }

  if (!response.ok) await parseError(response)
  if (response.status === 204) return null

  if (responseType === 'blob') {
    return {
      blob: await response.blob(),
      contentDisposition: response.headers.get('content-disposition'),
    }
  }

  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) return response.text()
  return response.json()
}

export async function login(credentials) {
  const session = await apiRequest('/v1/auth/login', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(credentials),
  })
  saveSession(session)
  return session
}

export async function register(payload) {
  const session = await apiRequest('/v1/auth/register', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload),
  })
  saveSession(session)
  return session
}

export async function logout() {
  const refreshToken = getRefreshToken()

  try {
    if (refreshToken) {
      await apiRequest('/v1/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refreshToken }),
      })
    }
  } catch {
    // Даже если Gateway недоступен, локальную сессию нужно завершить.
  } finally {
    clearSession()
  }
}

export async function getTasks() {
  const data = await apiRequest('/v1/tasks?page=0&size=50&sort=createdAt,desc')
  if (Array.isArray(data)) return data
  return data?.content || data?.items || data?.tasks || []
}

export function getTask(id) {
  return apiRequest(`/v1/tasks/${id}`)
}

export function getTaskStatus(id) {
  return apiRequest(`/v1/tasks/${id}/status`)
}

export function createTask({ file, station }) {
  const formData = new FormData()
  formData.append('file', file)

  // Текущий Gateway принимает только file. Дополнительное поле не ломает
  // multipart-запрос и уже готово к будущей поддержке station на бэкенде.
  formData.append('station', station)

  return apiRequest('/v1/tasks', {
    method: 'POST',
    body: formData,
  })
}

export function deleteTask(id) {
  return apiRequest(`/v1/tasks/${id}`, { method: 'DELETE' })
}

export async function downloadTask(id, fallbackName = 'instruction.pdf') {
  const { blob, contentDisposition } = await apiRequest(`/v1/tasks/${id}/download`, {
    responseType: 'blob',
  })

  const encodedName = contentDisposition?.match(/filename\*=UTF-8''([^;]+)/i)?.[1]
  const simpleName = contentDisposition?.match(/filename="?([^";]+)"?/i)?.[1]
  const fileName = encodedName
    ? decodeURIComponent(encodedName)
    : simpleName || fallbackName

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
