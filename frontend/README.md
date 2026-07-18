# Авто Инструкция — frontend

React/Vite-фронтенд сервиса генерации железнодорожных инструкций по техническому паспорту.

Фронтенд обращается только к Gateway. Напрямую с Parser Service, AI Service, Assembler Service, RabbitMQ и MinIO браузер не работает.

## Реализовано

- регистрация и вход через JWT;
- автоматическое обновление access-токена через refresh-токен;
- выход из аккаунта;
- загрузка PDF, DOC и DOCX;
- выбор станции;
- список задач пользователя;
- получение статуса задачи каждые 2,5 секунды;
- отображение этапов обработки;
- удаление задачи;
- скачивание готового PDF;
- адаптивный интерфейс.

## Структура

```text
frontend/
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
└── src/
    ├── api.js
    ├── App.jsx
    ├── constants.js
    ├── main.jsx
    └── styles.css
```

## Требования

- Node.js 18 или новее;
- npm;
- запущенный Gateway на `http://localhost:8080`.

Gateway предоставляет:

- `POST /api/v1/auth/register`;
- `POST /api/v1/auth/login`;
- `POST /api/v1/auth/refresh`;
- `POST /api/v1/auth/logout`;
- `POST /api/v1/tasks`;
- `GET /api/v1/tasks`;
- `GET /api/v1/tasks/{id}/status`;
- `GET /api/v1/tasks/{id}/download`;
- `DELETE /api/v1/tasks/{id}`.

## Запуск

```bash
npm install
npm run dev
```

Открыть:

```text
http://localhost:5173
```

Vite проксирует запросы `/api` на `http://localhost:8080`, поэтому для локальной разработки CORS не мешает работе.

## Переменные окружения

Создать `.env` из примера:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

По умолчанию:

```env
VITE_API_URL=/api
VITE_GATEWAY_TARGET=http://localhost:8080
```

## Проверка сборки

```bash
npm run build
npm run preview
```

## Важное ограничение текущего Gateway

На момент подключения `POST /api/v1/tasks` документирован только с multipart-полем `file`. Фронтенд также отправляет поле `station` и сохраняет выбранную станцию локально по `taskId`, но Gateway должен начать сохранять и передавать `station` другим сервисам.

Также Gateway пока не предоставляет endpoint с текстом или JSON готовой инструкции. Поэтому редактирование текста в браузере не реализовано: сейчас итог выдаётся как PDF через `/download`.
