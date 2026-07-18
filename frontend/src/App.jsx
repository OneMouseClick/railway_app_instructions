import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  createTask,
  deleteTask,
  downloadTask,
  getTaskStatus,
  getTasks,
  hasSession,
  login,
  logout,
  register,
} from './api'
import { PROCESSING_STEPS, STATIONS, STATUS_META, TERMINAL_STATUSES } from './constants'

const PROFILE_KEY = 'railway-user-profile'
const STATION_MAP_KEY = 'railway-task-stations'

function readJson(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

function saveProfile(profile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile))
}

function formatDate(value) {
  if (!value) return 'Дата не указана'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function getTaskFileName(task) {
  return task.originalFileName || task.fileName || task.filename || 'Технический паспорт'
}

function getTaskId(task) {
  return task.id || task.taskId
}

function getTaskStatusValue(task) {
  return task.status || 'CREATED'
}

function taskTitle(task) {
  return getTaskFileName(task).replace(/\.[^.]+$/, '')
}

function normalizeStatusResponse(previousTask, response) {
  if (typeof response === 'string') return { ...previousTask, status: response }
  return { ...previousTask, ...response }
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-.7 11H7.7L7 9Zm3 2v7h2v-7h-2Zm4 0v7h2v-7h-2Z" />
    </svg>
  )
}

function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    firstName: '',
    lastName: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      if (mode === 'login') {
        await login({ username: form.username.trim(), password: form.password })
        onAuthenticated({ username: form.username.trim() })
      } else {
        await register({
          username: form.username.trim(),
          email: form.email.trim(),
          password: form.password,
          firstName: form.firstName.trim(),
          lastName: form.lastName.trim(),
        })
        onAuthenticated({
          username: form.username.trim(),
          firstName: form.firstName.trim(),
          lastName: form.lastName.trim(),
        })
      }
    } catch (requestError) {
      setError(requestError.message || 'Не удалось выполнить запрос.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="brand-mark">РЖД</div>
          <div>
            <strong>Авто Инструкция</strong>
            <span>Генерация документов по техническим паспортам</span>
          </div>
        </div>

        <div className="auth-tabs" role="tablist" aria-label="Авторизация">
          <button
            type="button"
            className={mode === 'login' ? 'auth-tab-active' : ''}
            onClick={() => {
              setMode('login')
              setError('')
            }}
          >
            Вход
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'auth-tab-active' : ''}
            onClick={() => {
              setMode('register')
              setError('')
            }}
          >
            Регистрация
          </button>
        </div>

        <div className="auth-heading">
          <h1>{mode === 'login' ? 'Войдите в систему' : 'Создайте аккаунт'}</h1>
          <p>
            {mode === 'login'
              ? 'Используйте имя пользователя и пароль.'
              : 'Заполните данные, чтобы начать работу с инструкциями.'}
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div className="auth-row">
              <label>
                <span>Имя</span>
                <input
                  name="firstName"
                  value={form.firstName}
                  onChange={updateField}
                  autoComplete="given-name"
                  required
                />
              </label>
              <label>
                <span>Фамилия</span>
                <input
                  name="lastName"
                  value={form.lastName}
                  onChange={updateField}
                  autoComplete="family-name"
                  required
                />
              </label>
            </div>
          )}

          <label>
            <span>Имя пользователя</span>
            <input
              name="username"
              value={form.username}
              onChange={updateField}
              autoComplete="username"
              minLength={3}
              required
            />
          </label>

          {mode === 'register' && (
            <label>
              <span>Email</span>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={updateField}
                autoComplete="email"
                required
              />
            </label>
          )}

          <label>
            <span>Пароль</span>
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={updateField}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={8}
              required
            />
          </label>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="primary-button wide-button" disabled={submitting}>
            {submitting
              ? 'Отправка…'
              : mode === 'login'
                ? 'Войти'
                : 'Зарегистрироваться'}
          </button>
        </form>
      </section>
    </main>
  )
}

function UploadCard({ file, setFile }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  function validateAndSet(nextFile) {
    if (!nextFile) return
    const extension = nextFile.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'doc', 'docx'].includes(extension)) {
      window.alert('Поддерживаются только PDF, DOC и DOCX')
      return
    }
    setFile(nextFile)
  }

  return (
    <div
      className={`upload-card ${dragging ? 'upload-card-dragging' : ''}`}
      onDragOver={(event) => {
        event.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault()
        setDragging(false)
        validateAndSet(event.dataTransfer.files?.[0])
      }}
    >
      <input
        ref={inputRef}
        hidden
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={(event) => validateAndSet(event.target.files?.[0])}
      />

      {!file ? (
        <>
          <div className="upload-icon">⇧</div>
          <h3>Загрузите технический паспорт</h3>
          <p>PDF, DOC или DOCX</p>
          <button type="button" className="secondary-button" onClick={() => inputRef.current?.click()}>
            Выбрать файл
          </button>
        </>
      ) : (
        <div className="selected-file">
          <div className="file-icon">DOC</div>
          <div>
            <strong>{file.name}</strong>
            <span>{Math.max(1, Math.round(file.size / 1024))} КБ</span>
          </div>
          <button type="button" className="text-button" onClick={() => setFile(null)}>
            Удалить
          </button>
        </div>
      )}
    </div>
  )
}

function NewInstructionView({ onCreate }) {
  const [station, setStation] = useState(STATIONS[0])
  const [file, setFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleCreate() {
    if (!file) return
    setSubmitting(true)
    setError('')

    try {
      await onCreate({ station, file })
    } catch (requestError) {
      setError(requestError.message || 'Не удалось загрузить документ.')
      setSubmitting(false)
    }
  }

  return (
    <main className="workspace center-workspace">
      <section className="new-card">
        <h1>Создайте инструкцию по техническому паспорту</h1>
        <p className="lead">Выберите станцию и загрузите паспорт железнодорожного пути.</p>

        <label className="field-label" htmlFor="station">
          Железнодорожная станция
        </label>
        <select
          id="station"
          className="select"
          value={station}
          onChange={(event) => setStation(event.target.value)}
        >
          {STATIONS.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>

        <UploadCard file={file} setFile={setFile} />
        {error && <div className="form-error">{error}</div>}

        <button
          type="button"
          className="primary-button wide-button"
          disabled={!file || submitting}
          onClick={handleCreate}
        >
          {submitting ? 'Загружаем…' : 'Создать инструкцию'}
        </button>
      </section>
    </main>
  )
}

function ProcessingView({ task, station }) {
  const status = getTaskStatusValue(task)
  const meta = STATUS_META[status] || STATUS_META.CREATED
  const isFailed = status === 'FAILED'

  return (
    <main className="workspace chat-workspace">
      <div className="chat-shell">
        <div className="chat-message chat-message-user">
          <div className="chat-avatar">Вы</div>
          <div className="chat-bubble">
            <strong>Создать инструкцию для станции {station || 'не указана'}</strong>
            <span className="file-pill">📄 {getTaskFileName(task)}</span>
          </div>
        </div>

        <div className="chat-message">
          <div className="chat-avatar system-avatar">AI</div>
          <div className="chat-bubble system-bubble">
            <strong>{isFailed ? 'Не удалось обработать документ' : 'Обрабатываю технический паспорт'}</strong>
            <div className={`progress-track ${isFailed ? 'progress-track-error' : ''}`}>
              <div className="progress-value" style={{ width: `${meta.progress}%` }} />
            </div>
            <div className="progress-row">
              <span>{meta.label}</span>
              <strong>{meta.progress}%</strong>
            </div>

            <div className="steps">
              {PROCESSING_STEPS.map((step, index) => (
                <div
                  key={step}
                  className={`step ${index < meta.step ? 'step-done' : ''} ${
                    index === meta.step ? 'step-active' : ''
                  }`}
                >
                  <span>{index < meta.step ? '✓' : index + 1}</span>
                  {step}
                </div>
              ))}
            </div>

            {isFailed && (
              <div className="processing-error">
                {task.errorMessage || 'Gateway вернул статус FAILED без описания ошибки.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

function TaskView({ task, station, onDownload, onRefresh, downloading, refreshing }) {
  const status = getTaskStatusValue(task)
  const meta = STATUS_META[status] || STATUS_META.CREATED
  const completed = status === 'COMPLETED'
  const failed = status === 'FAILED'

  return (
    <main className="workspace task-workspace">
      <header className="editor-header">
        <div>
          <h1>{taskTitle(task)}</h1>
          <p>{station || 'Станция не сохранена'} · {getTaskFileName(task)}</p>
        </div>

        <div className="header-actions">
          <button type="button" className="secondary-button" onClick={onRefresh} disabled={refreshing}>
            {refreshing ? 'Обновление…' : 'Обновить статус'}
          </button>
          <button
            type="button"
            className="primary-button"
            onClick={onDownload}
            disabled={!completed || downloading}
          >
            {downloading ? 'Скачивание…' : 'Скачать PDF'}
          </button>
        </div>
      </header>

      <section className="task-content">
        <div className="task-hero">
          <div className={`status-icon ${completed ? 'status-icon-success' : failed ? 'status-icon-error' : ''}`}>
            {completed ? '✓' : failed ? '!' : '…'}
          </div>
          <div>
            <span className={`status-badge status-${status.toLowerCase()}`}>{meta.label}</span>
            <h2>
              {completed
                ? 'Инструкция готова к скачиванию'
                : failed
                  ? 'Обработка завершилась с ошибкой'
                  : 'Инструкция ещё формируется'}
            </h2>
            <p>
              {completed
                ? 'Gateway получил итоговый PDF от сервиса сборки.'
                : failed
                  ? task.errorMessage || 'Подробности ошибки не переданы.'
                  : 'Страница автоматически получает актуальный статус задачи.'}
            </p>
          </div>
        </div>

        <div className="task-grid">
          <div><span>Файл</span><strong>{getTaskFileName(task)}</strong></div>
          <div><span>Станция</span><strong>{station || 'Не указана'}</strong></div>
          <div><span>Статус</span><strong>{status}</strong></div>
          <div><span>Создана</span><strong>{formatDate(task.createdAt)}</strong></div>
          <div><span>Обновлена</span><strong>{formatDate(task.updatedAt)}</strong></div>
          <div><span>ID задачи</span><strong className="task-id">{getTaskId(task)}</strong></div>
        </div>
      </section>
    </main>
  )
}

function TaskItem({ task, station, active, onOpen, onDelete }) {
  const status = getTaskStatusValue(task)
  const meta = STATUS_META[status] || STATUS_META.CREATED

  return (
    <div className={`instruction-item ${active ? 'instruction-item-active' : ''}`}>
      <button type="button" className="instruction-open-button" onClick={onOpen}>
        <span className="instruction-item-title">{taskTitle(task)}</span>
        <span className="instruction-item-meta">{station || meta.label}</span>
        <span className="instruction-item-date">{formatDate(task.updatedAt || task.createdAt)}</span>
      </button>
      <button
        type="button"
        className="instruction-delete-button"
        aria-label={`Удалить задачу ${taskTitle(task)}`}
        title="Удалить задачу"
        onClick={onDelete}
      >
        <TrashIcon />
      </button>
    </div>
  )
}

function DeleteTaskModal({ task, onCancel, onConfirm, deleting }) {
  if (!task) return null

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onCancel}>
      <div
        className="confirm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-modal-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="confirm-modal-icon"><TrashIcon /></div>
        <h2 id="delete-modal-title">Удалить задачу?</h2>
        <p>Документ «{getTaskFileName(task)}» будет удалён без возможности восстановления.</p>
        <div className="confirm-modal-actions">
          <button type="button" className="secondary-button" onClick={onCancel} disabled={deleting}>
            Отмена
          </button>
          <button type="button" className="delete-confirm-button" onClick={onConfirm} disabled={deleting}>
            {deleting ? 'Удаление…' : 'Удалить'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(hasSession)
  const [profile, setProfile] = useState(() => readJson(PROFILE_KEY, {}))
  const [tasks, setTasks] = useState([])
  const [stationMap, setStationMap] = useState(() => readJson(STATION_MAP_KEY, {}))
  const [activeId, setActiveId] = useState(null)
  const [mode, setMode] = useState('new')
  const [loadingTasks, setLoadingTasks] = useState(false)
  const [loadError, setLoadError] = useState('')
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const activeTask = useMemo(
    () => tasks.find((task) => getTaskId(task) === activeId) || null,
    [tasks, activeId],
  )

  const updateTask = useCallback((id, patch) => {
    setTasks((current) => current.map((task) => (
      getTaskId(task) === id ? { ...task, ...patch } : task
    )))
  }, [])

  const loadTaskList = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoadingTasks(true)
    setLoadError('')

    try {
      const nextTasks = await getTasks()
      setTasks(nextTasks)

      setActiveId((currentId) => {
        if (currentId && nextTasks.some((task) => getTaskId(task) === currentId)) return currentId
        return nextTasks[0] ? getTaskId(nextTasks[0]) : null
      })
    } catch (error) {
      if (error.status === 401) {
        setAuthenticated(false)
      } else {
        setLoadError(error.message || 'Не удалось загрузить задачи.')
      }
    } finally {
      if (!silent) setLoadingTasks(false)
    }
  }, [])

  useEffect(() => {
    function handleUnauthorized() {
      setAuthenticated(false)
    }

    window.addEventListener('railway:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('railway:unauthorized', handleUnauthorized)
  }, [])

  useEffect(() => {
    if (authenticated) loadTaskList()
  }, [authenticated, loadTaskList])

  useEffect(() => {
    localStorage.setItem(STATION_MAP_KEY, JSON.stringify(stationMap))
  }, [stationMap])

  useEffect(() => {
    if (!activeTask) return undefined
    const status = getTaskStatusValue(activeTask)
    if (TERMINAL_STATUSES.has(status)) return undefined

    const timer = window.setInterval(async () => {
      try {
        const response = await getTaskStatus(getTaskId(activeTask))
        const updated = normalizeStatusResponse(activeTask, response)
        updateTask(getTaskId(activeTask), updated)
      } catch (error) {
        if (error.status !== 401) console.error(error)
      }
    }, 2500)

    return () => window.clearInterval(timer)
  }, [activeTask, updateTask])

  function handleAuthenticated(nextProfile) {
    saveProfile(nextProfile)
    setProfile(nextProfile)
    setAuthenticated(true)
    setMode('new')
  }

  async function handleLogout() {
    await logout()
    localStorage.removeItem(PROFILE_KEY)
    setAuthenticated(false)
    setProfile({})
    setTasks([])
    setActiveId(null)
  }

  async function handleCreate({ station, file }) {
    const createdTask = await createTask({ station, file })
    const id = getTaskId(createdTask)

    setStationMap((current) => ({ ...current, [id]: station }))
    setTasks((current) => [createdTask, ...current.filter((task) => getTaskId(task) !== id)])
    setActiveId(id)
    setMode('task')
  }

  async function handleRefreshTask() {
    if (!activeTask) return
    setRefreshing(true)

    try {
      const response = await getTaskStatus(getTaskId(activeTask))
      updateTask(getTaskId(activeTask), normalizeStatusResponse(activeTask, response))
    } catch (error) {
      window.alert(error.message || 'Не удалось обновить статус.')
    } finally {
      setRefreshing(false)
    }
  }

  async function handleDownload() {
    if (!activeTask) return
    setDownloading(true)

    try {
      const fallback = `${taskTitle(activeTask)}.pdf`
      await downloadTask(getTaskId(activeTask), fallback)
    } catch (error) {
      window.alert(error.message || 'Не удалось скачать PDF.')
    } finally {
      setDownloading(false)
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return
    const id = getTaskId(deleteTarget)
    setDeleting(true)

    try {
      await deleteTask(id)
      const nextTasks = tasks.filter((task) => getTaskId(task) !== id)
      setTasks(nextTasks)
      setStationMap((current) => {
        const next = { ...current }
        delete next[id]
        return next
      })
      setDeleteTarget(null)

      if (activeId === id) {
        const fallback = nextTasks[0]
        setActiveId(fallback ? getTaskId(fallback) : null)
        setMode(fallback ? 'task' : 'new')
      }
    } catch (error) {
      window.alert(error.message || 'Не удалось удалить задачу.')
    } finally {
      setDeleting(false)
    }
  }

  if (!authenticated) return <AuthPage onAuthenticated={handleAuthenticated} />

  const activeStatus = activeTask ? getTaskStatusValue(activeTask) : null
  const showProcessing = activeTask && !TERMINAL_STATUSES.has(activeStatus)

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">РЖД</div>
          <strong>Авто Инструкция</strong>
        </div>

        <button
          type="button"
          className="new-button"
          onClick={() => {
            setMode('new')
            setActiveId(null)
          }}
        >
          <span>＋</span> Новая инструкция
        </button>

        <div className="sidebar-section-title">Последние инструкции</div>

        <div className="instruction-list">
          {loadingTasks && <div className="sidebar-message">Загружаем…</div>}
          {!loadingTasks && loadError && (
            <button type="button" className="sidebar-retry" onClick={() => loadTaskList()}>
              {loadError}<br />Повторить
            </button>
          )}
          {!loadingTasks && !loadError && tasks.length === 0 && (
            <div className="sidebar-message">Пока нет загруженных документов</div>
          )}
          {tasks.map((task) => {
            const id = getTaskId(task)
            return (
              <TaskItem
                key={id}
                task={task}
                station={task.station || stationMap[id]}
                active={mode === 'task' && activeId === id}
                onOpen={() => {
                  setActiveId(id)
                  setMode('task')
                }}
                onDelete={() => setDeleteTarget(task)}
              />
            )
          })}
        </div>

        <div className="sidebar-user">
          <div className="user-avatar">
            {(profile.firstName || profile.username || 'U').slice(0, 1).toUpperCase()}
          </div>
          <div>
            <strong>{[profile.firstName, profile.lastName].filter(Boolean).join(' ') || profile.username}</strong>
            <span>{profile.username}</span>
          </div>
          <button type="button" onClick={handleLogout}>Выйти</button>
        </div>
      </aside>

      {mode === 'new' && <NewInstructionView onCreate={handleCreate} />}

      {mode === 'task' && activeTask && showProcessing && (
        <ProcessingView
          task={activeTask}
          station={activeTask.station || stationMap[getTaskId(activeTask)]}
        />
      )}

      {mode === 'task' && activeTask && !showProcessing && (
        <TaskView
          task={activeTask}
          station={activeTask.station || stationMap[getTaskId(activeTask)]}
          onDownload={handleDownload}
          onRefresh={handleRefreshTask}
          downloading={downloading}
          refreshing={refreshing}
        />
      )}

      {mode === 'task' && !activeTask && <NewInstructionView onCreate={handleCreate} />}

      <DeleteTaskModal
        task={deleteTarget}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        deleting={deleting}
      />
    </div>
  )
}
