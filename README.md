# Railway AI Platform

Платформа автоматической генерации технологических инструкций для железнодорожных станций (LLM + микросервисы).

## Структура monorepo

| Каталог | Сервис | Стек | Исходная ветка |
|---------|--------|------|----------------|
| `gateway/` | API Gateway, JWT, MinIO, RabbitMQ, PostgreSQL | Java 21, Spring Boot | `gateway` |
| `frontend/` | UI загрузки и работы с инструкциями | React 19, Vite | `frontend` |
| `document-service/` | Парсинг PDF/DOC/DOCX → JSON | Python, FastAPI | `parser_service` |
| `ai-service/` | Генерация текста инструкции (RAG + GigaChat) | Python, FastAPI | `AI_service` |
| `assembler-service/` | Сборка итогового документа | Python, python-docx | `assembler_service` |

## Рабочая ветка

Ветка `integration` — единая точка для дальнейшей интеграции сервисов через RabbitMQ и MinIO.

## Запуск всей платформы

```bash
docker compose up --build
```

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| Gateway API / Swagger | http://localhost:8080/swagger-ui.html |
| RabbitMQ UI | http://localhost:15672 (`railway` / `railway_secret`) |
| MinIO UI | http://localhost:9001 (`minioadmin` / `minioadmin`) |

Пайплайн: `POST /api/v1/tasks` → Document → AI (`AI_MOCK=true` по умолчанию) → Assembler → `GET /api/v1/tasks/{id}/download`.

Для реальной генерации через GigaChat: задайте `AI_MOCK=false` и `GIGACHAT_CREDENTIALS`, поднимите Qdrant, пересоберите `ai-service` с `requirements.txt`.
