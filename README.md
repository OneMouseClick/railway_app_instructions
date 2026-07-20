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

## Текущий статус

- Бизнес-логика сервисов собрана в одном репозитории.
- End-to-end пайплайн (события RabbitMQ + MinIO между сервисами) ещё не связан — следующий этап работы.
