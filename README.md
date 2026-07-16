```markdown
# Railway AI Platform — Gateway Service

Центральный микросервис платформы генерации технологических инструкций для железнодорожных станций.

**Стек:** Java 21, Spring Boot 3.3, PostgreSQL 16, RabbitMQ 3.13, MinIO, Docker

**Gateway отвечает за:**
- Регистрацию и аутентификацию пользователей (JWT)
- Приём документов от пользователей
- Хранение файлов в MinIO
- Управление жизненным циклом задач (статусы)
- Публикацию событий в RabbitMQ для других микросервисов
- Приём событий от микросервисов и обновление статусов задач
- Выдачу готовых PDF-инструкций пользователям

---

## Быстрый старт (первый запуск)

### 1. Что должно быть установлено

| Инструмент | Минимальная версия | Проверка |
|------------|-------------------|----------|
| Java JDK | 21 | `java -version` |
| Maven | 3.9+ | `mvn -version` |
| Docker | 24+ | `docker -v` |
| Docker Compose | 2+ | `docker-compose -v` |

### 2. Сборка и запуск

```powershell
# Перейти в корень проекта
cd M:\railway-gateway

# Собрать JAR
mvn clean package -DskipTests -pl gateway -am

# Запустить все контейнеры (PostgreSQL, RabbitMQ, MinIO, Gateway)
docker-compose -f docker-compose.dev.yml up -d --build
```

### 3. Проверка, что всё работает

```powershell
# Проверить, что все контейнеры запущены
docker ps

# Проверить health Gateway (в PowerShell)
curl http://localhost:8080/actuator/health
```

Ожидаемый ответ:
```json
{
  "status": "UP",
  "components": {
    "db": {"status": "UP"},
    "minio": {"status": "UP"},
    "rabbit": {"status": "UP"}
  }
}
```

### 4. Остановка

```powershell
# Остановить контейнеры (данные в БД и MinIO сохраняются)
docker-compose -f docker-compose.dev.yml down

# Остановить и удалить все данные — ПОЛНЫЙ СБРОС (БД очистится, файлы удалятся)
docker-compose -f docker-compose.dev.yml down -v
```

### 5. Пересборка после изменений кода

```powershell
mvn clean package -DskipTests -pl gateway -am
docker-compose -f docker-compose.dev.yml up -d --build
```

Пересобирается только Gateway. PostgreSQL, RabbitMQ и MinIO не перезапускаются, данные сохраняются.

---

## Доступы и URL'ы

| Сервис | URL | Логин | Пароль |
|--------|-----|-------|--------|
| **Gateway API** | http://localhost:8080 | — | — |
| **Swagger UI** | http://localhost:8080/swagger-ui.html | — | — |
| **Health Check** | http://localhost:8080/actuator/health | — | — |
| **PostgreSQL** | `localhost:5432` | `railway` | `railway_secret` |
| **RabbitMQ Management** | http://localhost:15672 | `railway` | `railway_secret` |
| **MinIO API (S3)** | http://localhost:9000 | `minioadmin` | `minioadmin` |
| **MinIO Console (Web UI)** | http://localhost:9001 | `minioadmin` | `minioadmin` |

---

## Подключение к PostgreSQL

### Вариант 1: DBeaver (рекомендуется)

1. Скачай и установи [DBeaver](https://dbeaver.io/) (бесплатный)
2. Нажми **Новое соединение** → выбери **PostgreSQL**
3. Заполни поля:

| Поле | Значение |
|------|----------|
| Host | `localhost` |
| Port | `5432` |
| Database | `railway_gateway` |
| Username | `railway` |
| Password | `railway_secret` |

4. Нажми **Test Connection** → должно быть "Connected"
5. Нажми **Finish**

**Основные таблицы:**
- `users` — зарегистрированные пользователи
- `tasks` — задачи (статусы, ссылки на файлы в MinIO)
- `refresh_tokens` — JWT refresh-токены
- `flyway_schema_history` — история миграций

**Полезные SQL-запросы:**
```sql
-- Все пользователи
SELECT id, username, email, role, created_at FROM users;

-- Все задачи конкретного пользователя
SELECT id, status, original_file_name, error_message, 
       minio_object_name, parsed_content_object_key,
       generated_instruction_object_key, result_minio_object_name,
       created_at, updated_at
FROM tasks 
WHERE user_id = 'UUID-пользователя' 
ORDER BY created_at DESC;

-- Задачи по статусу
SELECT id, status, original_file_name, updated_at 
FROM tasks 
WHERE status = 'CREATED';

-- Все refresh-токены
SELECT id, user_id, revoked, expires_at FROM refresh_tokens;
```

### Вариант 2: Командная строка (psql в Docker)

```powershell
# Подключиться к PostgreSQL внутри контейнера
docker exec -it railway-postgres psql -U railway -d railway_gateway
```

После входа доступны команды:
```
\dt              — показать все таблицы
\d tasks         — структура таблицы tasks
\q               — выйти
```

Пример запроса:
```sql
SELECT id, status, original_file_name, created_at 
FROM tasks 
ORDER BY created_at DESC 
LIMIT 5;
```

### Где брать UUID'ы (taskId, userId, correlationId)

| Идентификатор | Где взять |
|---------------|-----------|
| **taskId** | Ответ `POST /api/v1/tasks` → поле `id`. Или `SELECT id FROM tasks ORDER BY created_at DESC LIMIT 1` |
| **userId** | Ответ `POST /api/v1/auth/register` — посмотреть в БД: `SELECT id FROM users WHERE username='testuser'` |
| **correlationId** | Всегда равен `taskId` в текущей реализации |
| **eventId** | Генерируется автоматически при публикации события. Можно посмотреть в RabbitMQ → сообщение → поле `eventId` |

---

## RabbitMQ — Управление и отладка

### Web UI

Открой http://localhost:15672 → логин `railway`, пароль `railway_secret`

### Основные разделы

| Вкладка | Что показывает |
|---------|----------------|
| **Overview** | Общее состояние: connections, channels, exchanges, queues |
| **Connections** | Кто подключён к RabbitMQ |
| **Exchanges** | Точки обмена сообщениями |
| **Queues** | Очереди сообщений |

### Exchanges (вкладка Exchanges)

| Exchange | Тип | Назначение |
|----------|-----|------------|
| `document.exchange` | topic | События для Document Service, AI Service, Assembler Service |
| `task.exchange` | topic | События изменения статусов задач (слушает Gateway) |
| `dead.letter.exchange` | topic | Сообщения, которые не удалось обработать |

### Queues (вкладка Queues)

| Queue | Назначение | Кто читает |
|-------|------------|------------|
| `document.parse.queue` | События создания задачи | Document Service (Python) |
| `ai.analyze.queue` | Зарезервировано | AI Service (Python) |
| `assemble.document.queue` | Зарезервировано | Assembler Service (Python) |
| `task.status.queue` | События изменения статусов | **Gateway (Java)** |
| `dead.letter.queue` | Необработанные сообщения | Никто (для отладки) |
| `retry.queue` | Сообщения на повторную обработку | Автоматически |

### Как посмотреть сообщение в очереди

1. Вкладка **Queues** → нажми на очередь (например `task.status.queue`)
2. Прокрути вниз до секции **Get Message**
3. Нажми **Get Message(s)** — покажет одно сообщение
4. В поле **Payload** увидишь JSON события

### Ready, Unacked, Total

| Показатель | Значение |
|------------|----------|
| **Ready** | Сообщения ждут обработки |
| **Unacked** | Сообщения доставлены потребителю, но он ещё не подтвердил (ack) |
| **Total** | Ready + Unacked |

Если сообщение надолго зависло в Unacked — потребитель не отвечает или упал.

### Как вручную опубликовать событие (симуляция микросервисов)

1. Вкладка **Exchanges** → нажми на `task.exchange`
2. Прокрути вниз до секции **Publish Message**
3. Заполни:
   - **Routing key:** `task.status`
   - **Headers:** оставь пустым
   - **Payload:** вставь JSON события (шаблоны ниже)
4. Нажми **Publish**

---

## MinIO — Файловое хранилище

### Web UI (Console)

Открой http://localhost:9001 → логин `minioadmin`, пароль `minioadmin`

### Bucket'ы

| Bucket | Для чего | Кто пишет | Кто читает |
|--------|----------|-----------|------------|
| `source-documents` | Исходные PDF/DOCX/PNG от пользователя | Gateway | Document Service |
| `parsed-json` | Распарсенный текст в JSON | Document Service | AI Service |
| `generated-json` | Сгенерированная инструкция в JSON | AI Service | Assembler Service |
| `result-documents` | Готовый PDF для скачивания | Assembler Service | Gateway |

Все 4 bucket'а создаются автоматически при старте Gateway.

### Формат ключей (ObjectKey)

```
{bucket}/
  └── {год}/
      └── {месяц}/
          └── {taskId}/
              └── {тип}/
                  └── {uuid}.{расширение}
```

**Примеры:**
- `source-documents/2026/07/5de02bd9.../source/a1b2c3d4.pdf`
- `parsed-json/2026/07/5de02bd9.../parsed/e5f6g7h8.json`
- `generated-json/2026/07/5de02bd9.../generated/i9j0k1l2.json`
- `result-documents/2026/07/5de02bd9.../result/m3n4o5p6.pdf`

---

## Руководство для фронтенд-разработчика

### Авторизация

Все запросы к `/api/v1/tasks/**` требуют JWT-токен.

**Регистрация:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"testuser@railway.com","password":"securePassword123","firstName":"Test","lastName":"User"}'
```

**Логин:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"securePassword123"}'
```

Ответ обоих запросов:
```json
{
  "accessToken": "eyJhbGciOiJIUzM4NCJ9...",
  "refreshToken": "...",
  "expiresIn": 900000,
  "tokenType": "Bearer"
}
```

### Использование токена

Все защищённые запросы должны содержать заголовок:
```
Authorization: Bearer <accessToken>
```

Access-токен живёт **15 минут**. Когда истекает — обновить:
```bash
curl -X POST http://localhost:8080/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken":"<refreshToken>"}'
```

### Основные API-эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/api/v1/tasks` | Загрузить документ (multipart/form-data, поле `file`) |
| `GET` | `/api/v1/tasks` | Список задач (пагинация, фильтрация) |
| `GET` | `/api/v1/tasks/{id}` | Детали задачи |
| `GET` | `/api/v1/tasks/{id}/status` | Только статус задачи |
| `GET` | `/api/v1/tasks/{id}/download` | Скачать готовый PDF |
| `DELETE` | `/api/v1/tasks/{id}` | Удалить задачу |

### Параметры для GET /api/v1/tasks

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `page` | int | `0` | Номер страницы |
| `size` | int | `10` | Размер страницы |
| `sort` | string | `createdAt,desc` | Поле и направление сортировки |
| `status` | string | — | Фильтр: `CREATED`, `PARSING`, `PARSED`, `GENERATING`, `GENERATED`, `ASSEMBLING`, `COMPLETED`, `FAILED` |
| `createdFrom` | ISO 8601 | — | Задачи созданные после даты |
| `createdTo` | ISO 8601 | — | Задачи созданные до даты |

**Пример:**
```
GET /api/v1/tasks?page=0&size=10&status=COMPLETED&sort=createdAt,desc&createdFrom=2026-07-01T00:00:00&createdTo=2026-07-31T23:59:59
```

### Статусы задачи

| Статус | Значение | resultAvailable |
|--------|----------|-----------------|
| `CREATED` | Задача создана, файл загружен | `false` |
| `PARSING` | Document Service парсит документ | `false` |
| `PARSED` | Документ распарсен | `false` |
| `GENERATING` | AI Service генерирует инструкцию | `false` |
| `GENERATED` | Инструкция сгенерирована | `false` |
| `ASSEMBLING` | Assembler Service собирает PDF | `false` |
| `COMPLETED` | PDF готов к скачиванию | **`true`** |
| `FAILED` | Ошибка обработки | `false` |

### Polling статуса

Фронтенд должен опрашивать `GET /api/v1/tasks/{id}/status` каждые 2-3 секунды, пока:
- `status == "COMPLETED"` → вызвать `GET /api/v1/tasks/{id}/download`
- `status == "FAILED"` → показать `errorMessage`

Поле `resultAvailable` в `TaskDetailsResponse` станет `true` только когда статус = `COMPLETED`.

### Swagger

Полная документация API с возможностью тестирования: http://localhost:8080/swagger-ui.html

**Как авторизоваться в Swagger:**
1. Выполни `POST /api/v1/auth/register` или `POST /api/v1/auth/login`
2. Скопируй `accessToken` из ответа
3. Нажми кнопку **Authorize** (замок справа вверху)
4. Вставь: `Bearer <accessToken>`
5. Нажми **Authorize** → **Close**

---

## Симуляция работы микросервисов (ручная отладка полного цикла)

Когда Document Service, AI Service и Assembler Service ещё не готовы, можно вручную провести задачу через весь жизненный цикл, публикуя события в RabbitMQ Management.

### Шаг 1: Получить taskId

Создай задачу через Swagger (`POST /api/v1/tasks`) и скопируй `id` из ответа.

**Пример:** `5de02bd9-9663-4bc3-bd41-9383bf925b32`

### Шаг 2: Отправить события по порядку

Открой http://localhost:15672 → вкладка **Exchanges** → `task.exchange` → **Publish Message**

**Routing key для всех событий:** `task.status`

**Подставь свой taskId** во все `taskId`, `correlationId` и пути `ObjectKey`.

#### 1. PARSING_STARTED
```json
{
  "eventType": "PARSING_STARTED",
  "eventId": "e1f2a3b4-c5d6-7890-abcd-ef1234567890",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:00:00Z"
}
```
**Проверка:** статус → `PARSING`

#### 2. PARSED
```json
{
  "eventType": "PARSED",
  "eventId": "f2a3b4c5-d6e7-8901-bcde-f12345678901",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:01:00Z",
  "parsedContentObjectKey": "2026/07/5de02bd9-9663-4bc3-bd41-9383bf925b32/parsed/test.json"
}
```
**Проверка:** статус → `PARSED`

#### 3. GENERATING_STARTED
```json
{
  "eventType": "GENERATING_STARTED",
  "eventId": "a3b4c5d6-e7f8-9012-cdef-123456789012",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:02:00Z"
}
```
**Проверка:** статус → `GENERATING`

#### 4. GENERATED
```json
{
  "eventType": "GENERATED",
  "eventId": "b4c5d6e7-f8a9-0123-defa-234567890123",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:03:00Z",
  "generatedInstructionObjectKey": "2026/07/5de02bd9-9663-4bc3-bd41-9383bf925b32/generated/test.json"
}
```
**Проверка:** статус → `GENERATED`

#### 5. ASSEMBLING_STARTED
```json
{
  "eventType": "ASSEMBLING_STARTED",
  "eventId": "c5d6e7f8-a9b0-1234-efab-345678901234",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:04:00Z"
}
```
**Проверка:** статус → `ASSEMBLING`

### Шаг 3: Загрузить тестовый PDF в MinIO

Перед отправкой `COMPLETED` нужно вручную загрузить PDF в MinIO:

1. Открой http://localhost:9001 → `minioadmin` / `minioadmin`
2. Войди в bucket **result-documents**
3. Нажми **Upload** → выбери любой PDF-файл с компьютера
4. После загрузки нажми на файл правой кнопкой → **Rename**
5. Вставь путь: `2026/07/5de02bd9-9663-4bc3-bd41-9383bf925b32/result/test.pdf`

### Шаг 4: Отправить COMPLETED

#### 6. COMPLETED
```json
{
  "eventType": "COMPLETED",
  "eventId": "d6e7f8a9-b0c1-2345-fabc-456789012345",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:05:00Z",
  "resultMinioObjectName": "2026/07/5de02bd9-9663-4bc3-bd41-9383bf925b32/result/test.pdf"
}
```
**Проверка:** статус → `COMPLETED`

### Шаг 5: Скачать результат

`GET /api/v1/tasks/5de02bd9-9663-4bc3-bd41-9383bf925b32/download` → скачается PDF

### Бонус: FAILED (симуляция ошибки)

```json
{
  "eventType": "FAILED",
  "eventId": "e7f8a9b0-c1d2-3456-abcd-567890123456",
  "correlationId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "taskId": "5de02bd9-9663-4bc3-bd41-9383bf925b32",
  "timestamp": "2026-07-16T12:06:00Z",
  "errorMessage": "Document parsing failed: invalid PDF structure"
}
```
**Проверка:** статус → `FAILED`, `GET /api/v1/tasks/{id}/download` → 409

---

## Просмотр логов Gateway

```powershell
# Все логи
docker logs railway-gateway

# Логи в реальном времени (Ctrl+C чтобы выйти)
docker logs -f railway-gateway

# Последние 100 строк
docker logs --tail 100 railway-gateway
```

**Ключевые строки в логах:**

| Строка | Значение |
|--------|----------|
| `Task created successfully: taskId=...` | Задача создана |
| `Publishing event: type=TASK_CREATED` | Событие отправлено в RabbitMQ |
| `Received event: type=PARSING_STARTED` | Gateway получил событие |
| `Task status updated: oldStatus=..., newStatus=...` | Статус изменился |
| `Task not found for ... event: taskId=...` | Событие для несуществующей задачи — проверь taskId |

---

## Запуск тестов

```powershell
# Все тесты
mvn test -pl gateway -am

# Конкретный тестовый класс
mvn test -pl gateway -am -Dtest=AuthControllerIntegrationTest

# Конкретный метод
mvn test -pl gateway -am -Dtest=AuthControllerIntegrationTest#shouldRegisterUserSuccessfully
```

**Требование:** Docker должен быть запущен (Testcontainers поднимает контейнеры автоматически).

### Сводка по тестам (41 сценарий)

| Тестовый класс | Сценариев | Что проверяет |
|----------------|-----------|---------------|
| `AuthControllerIntegrationTest` | 8 | Регистрация, дубликаты, логин, неверный пароль, refresh, revoked refresh, logout |
| `TaskControllerIntegrationTest` | 20 | Создание, валидация, детали, статус, список, фильтрация, пагинация, чужая задача, удаление, скачивание, 401 без JWT |
| `RabbitEventPublisherIntegrationTest` | 3 | Публикация, сериализация, routing key |
| `RabbitEventListenerIntegrationTest` | 6 | 5 типов событий + задача не найдена |
| `MinioServiceImplIntegrationTest` | 7 | Upload, download, delete, exists, copy, metadata |

---

## Структура проекта

```
railway-gateway/
├── pom.xml                          # Родительский POM
├── docker-compose.dev.yml           # Docker Compose для разработки
├── Dockerfile                       # Сборка образа Gateway
├── .gitignore
├── .dockerignore
├── README.md
└── gateway/
    ├── pom.xml                      # POM модуля Gateway
    └── src/
        ├── main/
        │   ├── java/com/railway/gateway/
        │   │   ├── GatewayApplication.java
        │   │   ├── api/              # Контроллеры и DTO
        │   │   │   ├── controller/
        │   │   │   │   ├── AuthController.java
        │   │   │   │   └── TaskController.java
        │   │   │   └── dto/          # Records: Request/Response DTO
        │   │   ├── application/      # Use cases, мапперы, валидаторы
        │   │   │   ├── mapper/
        │   │   │   ├── service/
        │   │   │   └── validator/
        │   │   ├── domain/           # Бизнес-логика (сущности, enums, исключения, интерфейсы)
        │   │   │   ├── entity/
        │   │   │   ├── enums/
        │   │   │   ├── event/
        │   │   │   ├── exception/
        │   │   │   ├── repository/
        │   │   │   ├── service/      # Интерфейсы (EventPublisher, MinioService)
        │   │   │   └── valueobject/
        │   │   └── infrastructure/   # Реализации (JPA, MinIO, RabbitMQ, Security)
        │   │       ├── config/
        │   │       ├── properties/
        │   │       ├── repository/
        │   │       ├── security/
        │   │       └── service/
        │   └── resources/
        │       ├── application.yml
        │       ├── application-dev.yml
        │       └── db/migration/     # Flyway миграции
        └── test/                     # Интеграционные тесты
```

---

## Полезные команды

```powershell
# Только собрать, без тестов
mvn clean package -DskipTests -pl gateway -am

# Запустить все тесты
mvn test -pl gateway -am

# Посмотреть дерево зависимостей
mvn dependency:tree -pl gateway

# Запустить Gateway локально (без Docker, инфраструктура должна быть запущена отдельно)
mvn spring-boot:run -pl gateway -am -Dspring-boot.run.profiles=dev
```
