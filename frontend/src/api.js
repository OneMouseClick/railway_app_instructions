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
  if (session?.accessToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, session.accessToken)
  }

  // При обновлении сессии Gateway может вернуть только новый accessToken.
  // В этом случае ранее выданный refreshToken сохраняется.
  if (session?.refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, session.refreshToken)
  }

  const expiresIn = Number(session?.expiresIn) || 900000
  localStorage.setItem(EXPIRES_AT_KEY, String(Date.now() + expiresIn))
}

export function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(EXPIRES_AT_KEY)
}

async function parseError(response) {
  let message = `Ошибка запроса: ${response.status}`
  let payload = null

  try {
    const raw = await response.text()
    if (raw) {
      try {
        payload = JSON.parse(raw)
      } catch {
        message = raw
      }
    }
  } catch {
    // Используем стандартное сообщение.
  }

  if (payload) {
    message = payload.message || payload.error || payload.detail || payload.title || message

    if (payload.errors && typeof payload.errors === 'object') {
      const validationMessage = Object.values(payload.errors).flat().join('. ')
      if (validationMessage) message = validationMessage
    }
  }

  const error = new Error(message)
  error.status = response.status
  error.data = payload
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
  const {
    auth = true,
    responseType = 'json',
    headers: customHeaders,
    ...fetchOptions
  } = options

  const headers = new Headers(customHeaders || {})
  const bodyIsFormData = fetchOptions.body instanceof FormData

  if (fetchOptions.body && !bodyIsFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (auth) {
    const accessToken = getAccessToken()
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)
  }

  let response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...fetchOptions,
      headers,
    })
  } catch {
    throw new Error('Gateway недоступен. Проверьте, что backend запущен.')
  }

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
      contentType: response.headers.get('content-type'),
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
  } finally {
    clearSession()
  }
}

export async function getTasks({ page = 0, size = 100 } = {}) {
  const data = await apiRequest(`/v1/tasks?page=${page}&size=${size}&sort=createdAt,desc`)
  if (Array.isArray(data)) return data
  return data?.content || data?.items || data?.tasks || []
}

export function getTaskStatus(id) {
  return apiRequest(`/v1/tasks/${encodeURIComponent(id)}/status`)
}

export function createTask({ file, station }) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('station', station)

  return apiRequest('/v1/tasks', {
    method: 'POST',
    body: formData,
  })
}

export function deleteTask(id) {
  return apiRequest(`/v1/tasks/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
}

export function getTaskContent(id) {
  return apiRequest(`/v1/tasks/${encodeURIComponent(id)}/content`)
}

export function saveTaskContent(id, payload) {
  return apiRequest(`/v1/tasks/${encodeURIComponent(id)}/content`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}
