# Авто Инструкция — frontend

Продовый React/Vite-фронтенд сервиса генерации железнодорожных инструкций по техническому паспорту.

Браузер обращается только к Gateway. Напрямую с Parser Service, AI Service, Assembler Service, RabbitMQ и MinIO фронтенд не работает.

## Реализовано

- регистрация и вход через JWT;
- автоматическое обновление access-токена через refresh-токен;
- выход из аккаунта;
- загрузка PDF, DOC и DOCX;
- выбор железнодорожной станции;
- список задач пользователя;
- polling всех незавершённых задач каждые 3 секунды;
- отображение этапов обработки и ошибок;
- получение и просмотр готовой инструкции;
- редактирование и сохранение текста через Gateway;
- экспорт текущей версии инструкции в PDF и DOCX;
- удаление задачи;
- предупреждение о несохранённых изменениях;
- адаптивный интерфейс.

Моковых задач, локальной генерации и демо-режима нет. Без доступного Gateway приложение показывает ошибку подключения.

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
    ├── documentExport.js
    ├── main.jsx
    └── styles.css
```

## Требования

- Node.js 18 или новее;
- npm;
- Gateway на `http://localhost:8080` для локальной разработки.

## Запуск

```bash
npm install
cp .env.example .env
npm run dev
```

На Windows PowerShell:

```powershell
Copy-Item .env.example .env
npm run dev
```

Открыть `http://localhost:5173`.

## Переменные окружения

```env
VITE_API_URL=/api
VITE_GATEWAY_TARGET=http://localhost:8080
```

Vite проксирует запросы `/api` на Gateway.

## Проверка сборки

```bash
npm run build
npm run preview
```

## Контракт Gateway

Авторизация:

- `POST /api/v1/auth/register`;
- `POST /api/v1/auth/login`;
- `POST /api/v1/auth/refresh`;
- `POST /api/v1/auth/logout`.

Задачи:

- `POST /api/v1/tasks` — multipart-поля `file` и `station`;
- `GET /api/v1/tasks`;
- `GET /api/v1/tasks/{id}/status`;
- `GET /api/v1/tasks/{id}/content`;
- `PUT /api/v1/tasks/{id}/content`;
- `DELETE /api/v1/tasks/{id}`.

Ожидаемые статусы:

```text
CREATED
PARSING
PARSED
GENERATING
GENERATED
ASSEMBLING
COMPLETED
FAILED
```

### Ответ `GET /api/v1/tasks/{id}/content`

```json
{
  "taskId": "uuid",
  "company": "ООО «Труд»",
  "station": "Благовещенск",
  "pathNumber": "без номера",
  "locomotives": "ТЭМ2, ТЭМ18",
  "connection": "стрелочным переводом №127 к пути №1",
  "boundary": "передний стык рамного рельса",
  "safety": "ручной сбрасывающий башмак БС №24",
  "content": "ИНСТРУКЦИЯ\n..."
}
```

`PUT /api/v1/tasks/{id}/content` принимает эти же редактируемые поля. Backend должен вернуть обновлённый объект либо ответить `204 No Content`.
