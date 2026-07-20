# Railway AI Platform тАФ Gateway Service

╨ж╨╡╨╜╤В╤А╨░╨╗╤М╨╜╤Л╨╣ ╨╝╨╕╨║╤А╨╛╤Б╨╡╤А╨▓╨╕╤Б ╨┐╨╗╨░╤В╤Д╨╛╤А╨╝╤Л ╨│╨╡╨╜╨╡╤А╨░╤Ж╨╕╨╕ ╤В╨╡╤Е╨╜╨╛╨╗╨╛╨│╨╕╤З╨╡╤Б╨║╨╕╤Е ╨╕╨╜╤Б╤В╤А╤Г╨║╤Ж╨╕╨╣ ╨┤╨╗╤П ╨╢╨╡╨╗╨╡╨╖╨╜╨╛╨┤╨╛╤А╨╛╨╢╨╜╤Л╤Е ╤Б╤В╨░╨╜╤Ж╨╕╨╣.

**╨б╤В╨╡╨║:** Java 21, Spring Boot 3.3, PostgreSQL 16, RabbitMQ 3.13, MinIO, Docker

**Gateway ╨╛╤В╨▓╨╡╤З╨░╨╡╤В ╨╖╨░:**
- ╨а╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╤О ╨╕ ╨░╤Г╤В╨╡╨╜╤В╨╕╤Д╨╕╨║╨░╤Ж╨╕╤О ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╡╨╣ (JWT)
- ╨Я╤А╨╕╤С╨╝ ╨┤╨╛╨║╤Г╨╝╨╡╨╜╤В╨╛╨▓ ╨╛╤В ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╡╨╣
- ╨е╤А╨░╨╜╨╡╨╜╨╕╨╡ ╤Д╨░╨╣╨╗╨╛╨▓ ╨▓ MinIO
- ╨г╨┐╤А╨░╨▓╨╗╨╡╨╜╨╕╨╡ ╨╢╨╕╨╖╨╜╨╡╨╜╨╜╤Л╨╝ ╤Ж╨╕╨║╨╗╨╛╨╝ ╨╖╨░╨┤╨░╤З (╤Б╤В╨░╤В╤Г╤Б╤Л)
- ╨Я╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╤О ╤Б╨╛╨▒╤Л╤В╨╕╨╣ ╨▓ RabbitMQ ╨┤╨╗╤П ╨┤╤А╤Г╨│╨╕╤Е ╨╝╨╕╨║╤А╨╛╤Б╨╡╤А╨▓╨╕╤Б╨╛╨▓
- ╨Я╤А╨╕╤С╨╝ ╤Б╨╛╨▒╤Л╤В╨╕╨╣ ╨╛╤В ╨╝╨╕╨║╤А╨╛╤Б╨╡╤А╨▓╨╕╤Б╨╛╨▓ ╨╕ ╨╛╨▒╨╜╨╛╨▓╨╗╨╡╨╜╨╕╨╡ ╤Б╤В╨░╤В╤Г╤Б╨╛╨▓ ╨╖╨░╨┤╨░╤З
- ╨Т╤Л╨┤╨░╤З╤Г ╨│╨╛╤В╨╛╨▓╤Л╤Е PDF-╨╕╨╜╤Б╤В╤А╤Г╨║╤Ж╨╕╨╣ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П╨╝

---

## ╨С╤Л╤Б╤В╤А╤Л╨╣ ╤Б╤В╨░╤А╤В (╨┐╨╡╤А╨▓╤Л╨╣ ╨╖╨░╨┐╤Г╤Б╨║)

### 1. ╨з╤В╨╛ ╨┤╨╛╨╗╨╢╨╜╨╛ ╨▒╤Л╤В╤М ╤Г╤Б╤В╨░╨╜╨╛╨▓╨╗╨╡╨╜╨╛

| ╨Ш╨╜╤Б╤В╤А╤Г╨╝╨╡╨╜╤В | ╨Ь╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╨░╤П ╨▓╨╡╤А╤Б╨╕╤П | ╨Я╤А╨╛╨▓╨╡╤А╨║╨░ |
|------------|-------------------|----------|
| Java JDK | 21 | `java -version` |
| Maven | 3.9+ | `mvn -version` |
| Docker | 24+ | `docker -v` |
| Docker Compose | 2+ | `docker-compose -v` |

### 2. ╨б╨▒╨╛╤А╨║╨░ ╨╕ ╨╖╨░╨┐╤Г╤Б╨║

```powershell
# ╨Я╨╡╤А╨╡╨╣╤В╨╕ ╨▓ ╨║╨╛╤А╨╡╨╜╤М ╨┐╤А╨╛╨╡╨║╤В╨░(╨╜╨░╨┐╤А╨╕╨╝╨╡╤А)
cd M:\railway-gateway

# ╨б╨╛╨▒╤А╨░╤В╤М JAR
mvn clean package -DskipTests -pl gateway -am

# ╨Ч╨░╨┐╤Г╤Б╤В╨╕╤В╤М ╨▓╤Б╨╡ ╨║╨╛╨╜╤В╨╡╨╣╨╜╨╡╤А╤Л (PostgreSQL, RabbitMQ, MinIO, Gateway)
docker-compose -f docker-compose.dev.yml up -d --build
```

### 3. ╨Я╤А╨╛╨▓╨╡╤А╨║╨░, ╤З╤В╨╛ ╨▓╤Б╤С ╤А╨░╨▒╨╛╤В╨░╨╡╤В

```powershell
# ╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М, ╤З╤В╨╛ ╨▓╤Б╨╡ ╨║╨╛╨╜╤В╨╡╨╣╨╜╨╡╤А╤Л ╨╖╨░╨┐╤Г╤Й╨╡╨╜╤Л
docker ps

# ╨Я╤А╨╛╨▓╨╡╤А╨╕╤В╤М health Gateway (╨▓ PowerShell)
curl http://localhost:8080/actuator/health
```

╨Ю╨╢╨╕╨┤╨░╨╡╨╝╤Л╨╣ ╨╛╤В╨▓╨╡╤В:
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

### 4. ╨Ю╤Б╤В╨░╨╜╨╛╨▓╨║╨░

```powershell
# ╨Ю╤Б╤В╨░╨╜╨╛╨▓╨╕╤В╤М ╨║╨╛╨╜╤В╨╡╨╣╨╜╨╡╤А╤Л (╨┤╨░╨╜╨╜╤Л╨╡ ╨▓ ╨С╨Ф ╨╕ MinIO ╤Б╨╛╤Е╤А╨░╨╜╤П╤О╤В╤Б╤П)
docker-compose -f docker-compose.dev.yml down

# ╨Ю╤Б╤В╨░╨╜╨╛╨▓╨╕╤В╤М ╨╕ ╤Г╨┤╨░╨╗╨╕╤В╤М ╨▓╤Б╨╡ ╨┤╨░╨╜╨╜╤Л╨╡ тАФ ╨Я╨Ю╨Ы╨Э╨л╨Щ ╨б╨С╨а╨Ю╨б (╨С╨Ф ╨╛╤З╨╕╤Б╤В╨╕╤В╤Б╤П, ╤Д╨░╨╣╨╗╤Л ╤Г╨┤╨░╨╗╤П╤В╤Б╤П)
docker-compose -f docker-compose.dev.yml down -v
```

### 5. ╨Я╨╡╤А╨╡╤Б╨▒╨╛╤А╨║╨░ ╨┐╨╛╤Б╨╗╨╡ ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╨╣ ╨║╨╛╨┤╨░

```powershell
mvn clean package -DskipTests -pl gateway -am
docker-compose -f docker-compose.dev.yml up -d --build
```

╨Я╨╡╤А╨╡╤Б╨╛╨▒╨╕╤А╨░╨╡╤В╤Б╤П ╤В╨╛╨╗╤М╨║╨╛ Gateway. PostgreSQL, RabbitMQ ╨╕ MinIO ╨╜╨╡ ╨┐╨╡╤А╨╡╨╖╨░╨┐╤Г╤Б╨║╨░╤О╤В╤Б╤П, ╨┤╨░╨╜╨╜╤Л╨╡ ╤Б╨╛╤Е╤А╨░╨╜╤П╤О╤В╤Б╤П.

---

## ╨Ф╨╛╤Б╤В╤Г╨┐╤Л ╨╕ URL'╤Л

| ╨б╨╡╤А╨▓╨╕╤Б | URL | ╨Ы╨╛╨│╨╕╨╜ | ╨Я╨░╤А╨╛╨╗╤М |
|--------|-----|-------|--------|
| **Gateway API** | http://localhost:8080 | тАФ | тАФ |
| **Swagger UI** | http://localhost:8080/swagger-ui.html | тАФ | тАФ |
| **Health Check** | http://localhost:8080/actuator/health | тАФ | тАФ |
| **PostgreSQL** | `localhost:5432` | `railway` | `railway_secret` |
| **RabbitMQ Management** | http://localhost:15672 | `railway` | `railway_secret` |
| **MinIO API (S3)** | http://localhost:9000 | `minioadmin` | `minioadmin` |
| **MinIO Console (Web UI)** | http://localhost:9001 | `minioadmin` | `minioadmin` |

---

## ╨Я╨╛╨┤╨║╨╗╤О╤З╨╡╨╜╨╕╨╡ ╨║ PostgreSQL

### ╨Т╨░╤А╨╕╨░╨╜╤В 1: DBeaver

╨Я╨╛╨╗╤П ╨┤╨╗╤П ╨┐╨╛╨┤╨║╨╗╤О╤З╨╡╨╜╨╕╤П:

| ╨Я╨╛╨╗╨╡ | ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ |
|------|----------|
| Host | `localhost` |
| Port | `5432` |
| Database | `railway_gateway` |
| Username | `railway` |
| Password | `railway_secret` |

**╨Ю╤Б╨╜╨╛╨▓╨╜╤Л╨╡ ╤В╨░╨▒╨╗╨╕╤Ж╤Л:**
- `users` тАФ ╨╖╨░╤А╨╡╨│╨╕╤Б╤В╤А╨╕╤А╨╛╨▓╨░╨╜╨╜╤Л╨╡ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╕
- `tasks` тАФ ╨╖╨░╨┤╨░╤З╨╕ (╤Б╤В╨░╤В╤Г╤Б╤Л, ╤Б╤Б╤Л╨╗╨║╨╕ ╨╜╨░ ╤Д╨░╨╣╨╗╤Л ╨▓ MinIO)
- `refresh_tokens` тАФ JWT refresh-╤В╨╛╨║╨╡╨╜╤Л
- `flyway_schema_history` тАФ ╨╕╤Б╤В╨╛╤А╨╕╤П ╨╝╨╕╨│╤А╨░╤Ж╨╕╨╣

**╨Я╨╛╨╗╨╡╨╖╨╜╤Л╨╡ SQL-╨╖╨░╨┐╤А╨╛╤Б╤Л:**
```sql
-- ╨Т╤Б╨╡ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╨╕
SELECT id, username, email, role, created_at FROM users;

-- ╨Т╤Б╨╡ ╨╖╨░╨┤╨░╤З╨╕ ╨║╨╛╨╜╨║╤А╨╡╤В╨╜╨╛╨│╨╛ ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П
SELECT id, status, original_file_name, error_message, 
       minio_object_name, parsed_content_object_key,
       generated_instruction_object_key, result_minio_object_name,
       created_at, updated_at
FROM tasks 
WHERE user_id = 'UUID-╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П' 
ORDER BY created_at DESC;

-- ╨Ч╨░╨┤╨░╤З╨╕ ╨┐╨╛ ╤Б╤В╨░╤В╤Г╤Б╤Г
SELECT id, status, original_file_name, updated_at 
FROM tasks 
WHERE status = 'CREATED';

-- ╨Т╤Б╨╡ refresh-╤В╨╛╨║╨╡╨╜╤Л
SELECT id, user_id, revoked, expires_at FROM refresh_tokens;
```

### ╨Т╨░╤А╨╕╨░╨╜╤В 2: ╨Ъ╨╛╨╝╨░╨╜╨┤╨╜╨░╤П ╤Б╤В╤А╨╛╨║╨░ (psql ╨▓ Docker)

```powershell
# ╨Я╨╛╨┤╨║╨╗╤О╤З╨╕╤В╤М╤Б╤П ╨║ PostgreSQL ╨▓╨╜╤Г╤В╤А╨╕ ╨║╨╛╨╜╤В╨╡╨╣╨╜╨╡╤А╨░
docker exec -it railway-postgres psql -U railway -d railway_gateway
```

╨Я╨╛╤Б╨╗╨╡ ╨▓╤Е╨╛╨┤╨░ ╨┤╨╛╤Б╤В╤Г╨┐╨╜╤Л ╨║╨╛╨╝╨░╨╜╨┤╤Л:
```
\dt              тАФ ╨┐╨╛╨║╨░╨╖╨░╤В╤М ╨▓╤Б╨╡ ╤В╨░╨▒╨╗╨╕╤Ж╤Л
\d tasks         тАФ ╤Б╤В╤А╤Г╨║╤В╤Г╤А╨░ ╤В╨░╨▒╨╗╨╕╤Ж╤Л tasks
\q               тАФ ╨▓╤Л╨╣╤В╨╕
```

╨Я╤А╨╕╨╝╨╡╤А ╨╖╨░╨┐╤А╨╛╤Б╨░:
```sql
SELECT id, status, original_file_name, created_at 
FROM tasks 
ORDER BY created_at DESC 
LIMIT 5;
```

### ╨У╨┤╨╡ ╨▒╤А╨░╤В╤М UUID'╤Л (taskId, userId, correlationId)

| ╨Ш╨┤╨╡╨╜╤В╨╕╤Д╨╕╨║╨░╤В╨╛╤А | ╨У╨┤╨╡ ╨▓╨╖╤П╤В╤М |
|---------------|-----------|
| **taskId** | ╨Ю╤В╨▓╨╡╤В `POST /api/v1/tasks` тЖТ ╨┐╨╛╨╗╨╡ `id`. ╨Ш╨╗╨╕ `SELECT id FROM tasks ORDER BY created_at DESC LIMIT 1` |
| **userId** | ╨Ю╤В╨▓╨╡╤В `POST /api/v1/auth/register` тАФ ╨┐╨╛╤Б╨╝╨╛╤В╤А╨╡╤В╤М ╨▓ ╨С╨Ф: `SELECT id FROM users WHERE username='testuser'` |
| **correlationId** | ╨Т╤Б╨╡╨│╨┤╨░ ╤А╨░╨▓╨╡╨╜ `taskId` ╨▓ ╤В╨╡╨║╤Г╤Й╨╡╨╣ ╤А╨╡╨░╨╗╨╕╨╖╨░╤Ж╨╕╨╕ |
| **eventId** | ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В╤Б╤П ╨░╨▓╤В╨╛╨╝╨░╤В╨╕╤З╨╡╤Б╨║╨╕ ╨┐╤А╨╕ ╨┐╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╨╕ ╤Б╨╛╨▒╤Л╤В╨╕╤П. ╨Ь╨╛╨╢╨╜╨╛ ╨┐╨╛╤Б╨╝╨╛╤В╤А╨╡╤В╤М ╨▓ RabbitMQ тЖТ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡ тЖТ ╨┐╨╛╨╗╨╡ `eventId` |

---

## RabbitMQ тАФ ╨г╨┐╤А╨░╨▓╨╗╨╡╨╜╨╕╨╡ ╨╕ ╨╛╤В╨╗╨░╨┤╨║╨░

### Web UI

╨Я╨╡╤А╨╡╨╣╤В╨╕ ╨╜╨░ http://localhost:15672 тЖТ ╨╗╨╛╨│╨╕╨╜ `railway`, ╨┐╨░╤А╨╛╨╗╤М `railway_secret`

### ╨Ю╤Б╨╜╨╛╨▓╨╜╤Л╨╡ ╤А╨░╨╖╨┤╨╡╨╗╤Л

| ╨Т╨║╨╗╨░╨┤╨║╨░ | ╨з╤В╨╛ ╨┐╨╛╨║╨░╨╖╤Л╨▓╨░╨╡╤В |
|---------|----------------|
| **Overview** | ╨Ю╨▒╤Й╨╡╨╡ ╤Б╨╛╤Б╤В╨╛╤П╨╜╨╕╨╡: connections, channels, exchanges, queues |
| **Connections** | ╨Ъ╤В╨╛ ╨┐╨╛╨┤╨║╨╗╤О╤З╤С╨╜ ╨║ RabbitMQ |
| **Exchanges** | ╨в╨╛╤З╨║╨╕ ╨╛╨▒╨╝╨╡╨╜╨░ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П╨╝╨╕ |
| **Queues** | ╨Ю╤З╨╡╤А╨╡╨┤╨╕ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╣ |

### Exchanges (╨▓╨║╨╗╨░╨┤╨║╨░ Exchanges)

| Exchange | ╨в╨╕╨┐ | ╨Э╨░╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡ |
|----------|-----|------------|
| `document.exchange` | topic | ╨б╨╛╨▒╤Л╤В╨╕╤П ╨┤╨╗╤П Document Service, AI Service, Assembler Service |
| `task.exchange` | topic | ╨б╨╛╨▒╤Л╤В╨╕╤П ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╤П ╤Б╤В╨░╤В╤Г╤Б╨╛╨▓ ╨╖╨░╨┤╨░╤З (╤Б╨╗╤Г╤И╨░╨╡╤В Gateway) |
| `dead.letter.exchange` | topic | ╨б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П, ╨║╨╛╤В╨╛╤А╤Л╨╡ ╨╜╨╡ ╤Г╨┤╨░╨╗╨╛╤Б╤М ╨╛╨▒╤А╨░╨▒╨╛╤В╨░╤В╤М |

### Queues (╨▓╨║╨╗╨░╨┤╨║╨░ Queues)

| Queue | ╨Э╨░╨╖╨╜╨░╤З╨╡╨╜╨╕╨╡ | ╨Ъ╤В╨╛ ╤З╨╕╤В╨░╨╡╤В |
|-------|------------|------------|
| `document.parse.queue` | ╨б╨╛╨▒╤Л╤В╨╕╤П ╤Б╨╛╨╖╨┤╨░╨╜╨╕╤П ╨╖╨░╨┤╨░╤З╨╕ | Document Service (Python) |
| `ai.analyze.queue` | ╨Ч╨░╤А╨╡╨╖╨╡╤А╨▓╨╕╤А╨╛╨▓╨░╨╜╨╛ | AI Service (Python) |
| `assemble.document.queue` | ╨Ч╨░╤А╨╡╨╖╨╡╤А╨▓╨╕╤А╨╛╨▓╨░╨╜╨╛ | Assembler Service (Python) |
| `task.status.queue` | ╨б╨╛╨▒╤Л╤В╨╕╤П ╨╕╨╖╨╝╨╡╨╜╨╡╨╜╨╕╤П ╤Б╤В╨░╤В╤Г╤Б╨╛╨▓ | **Gateway (Java)** |
| `dead.letter.queue` | ╨Э╨╡╨╛╨▒╤А╨░╨▒╨╛╤В╨░╨╜╨╜╤Л╨╡ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П | ╨Э╨╕╨║╤В╨╛ (╨┤╨╗╤П ╨╛╤В╨╗╨░╨┤╨║╨╕) |
| `retry.queue` | ╨б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П ╨╜╨░ ╨┐╨╛╨▓╤В╨╛╤А╨╜╤Г╤О ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╤Г | ╨Р╨▓╤В╨╛╨╝╨░╤В╨╕╤З╨╡╤Б╨║╨╕ |

### ╨Ъ╨░╨║ ╨┐╨╛╤Б╨╝╨╛╤В╤А╨╡╤В╤М ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡ ╨▓ ╨╛╤З╨╡╤А╨╡╨┤╨╕

1. ╨Т╨║╨╗╨░╨┤╨║╨░ **Queues** тЖТ ╨╜╨░╨╢╨╝╨╕ ╨╜╨░ ╨╛╤З╨╡╤А╨╡╨┤╤М (╨╜╨░╨┐╤А╨╕╨╝╨╡╤А `task.status.queue`)
2. ╨Я╤А╨╛╨║╤А╤Г╤В╨╕ ╨▓╨╜╨╕╨╖ ╨┤╨╛ ╤Б╨╡╨║╤Ж╨╕╨╕ **Get Message**
3. ╨Э╨░╨╢╨╝╨╕ **Get Message(s)** тАФ ╨┐╨╛╨║╨░╨╢╨╡╤В ╨╛╨┤╨╜╨╛ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡
4. ╨Т ╨┐╨╛╨╗╨╡ **Payload** ╤Г╨▓╨╕╨┤╨╕╤И╤М JSON ╤Б╨╛╨▒╤Л╤В╨╕╤П

### Ready, Unacked, Total

| ╨Я╨╛╨║╨░╨╖╨░╤В╨╡╨╗╤М | ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ |
|------------|----------|
| **Ready** | ╨б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П ╨╢╨┤╤Г╤В ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╕ |
| **Unacked** | ╨б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П ╨┤╨╛╤Б╤В╨░╨▓╨╗╨╡╨╜╤Л ╨┐╨╛╤В╤А╨╡╨▒╨╕╤В╨╡╨╗╤О, ╨╜╨╛ ╨╛╨╜ ╨╡╤Й╤С ╨╜╨╡ ╨┐╨╛╨┤╤В╨▓╨╡╤А╨┤╨╕╨╗ (ack) |
| **Total** | Ready + Unacked |

╨Х╤Б╨╗╨╕ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╡ ╨╜╨░╨┤╨╛╨╗╨│╨╛ ╨╖╨░╨▓╨╕╤Б╨╗╨╛ ╨▓ Unacked тАФ ╨┐╨╛╤В╤А╨╡╨▒╨╕╤В╨╡╨╗╤М ╨╜╨╡ ╨╛╤В╨▓╨╡╤З╨░╨╡╤В ╨╕╨╗╨╕ ╤Г╨┐╨░╨╗.

### ╨Ъ╨░╨║ ╨▓╤А╤Г╤З╨╜╤Г╤О ╨╛╨┐╤Г╨▒╨╗╨╕╨║╨╛╨▓╨░╤В╤М ╤Б╨╛╨▒╤Л╤В╨╕╨╡ (╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╤П ╨╝╨╕╨║╤А╨╛╤Б╨╡╤А╨▓╨╕╤Б╨╛╨▓)

1. ╨Т╨║╨╗╨░╨┤╨║╨░ **Exchanges** тЖТ ╨╜╨░╨╢╨╝╨╕ ╨╜╨░ `task.exchange`
2. ╨Я╤А╨╛╨║╤А╤Г╤В╨╕ ╨▓╨╜╨╕╨╖ ╨┤╨╛ ╤Б╨╡╨║╤Ж╨╕╨╕ **Publish Message**
3. ╨Ч╨░╨┐╨╛╨╗╨╜╨╕:
   - **Routing key:** `task.status`
   - **Headers:** ╨╛╤Б╤В╨░╨▓╤М ╨┐╤Г╤Б╤В╤Л╨╝
   - **Payload:** ╨▓╤Б╤В╨░╨▓╤М JSON ╤Б╨╛╨▒╤Л╤В╨╕╤П (╤И╨░╨▒╨╗╨╛╨╜╤Л ╨╜╨╕╨╢╨╡)
4. ╨Э╨░╨╢╨╝╨╕ **Publish**

---

## MinIO тАФ ╨д╨░╨╣╨╗╨╛╨▓╨╛╨╡ ╤Е╤А╨░╨╜╨╕╨╗╨╕╤Й╨╡

### Web UI (Console)

╨Ю╤В╨║╤А╨╛╨╣ http://localhost:9001 тЖТ ╨╗╨╛╨│╨╕╨╜ `minioadmin`, ╨┐╨░╤А╨╛╨╗╤М `minioadmin`

### Bucket'╤Л

| Bucket | ╨Ф╨╗╤П ╤З╨╡╨│╨╛ | ╨Ъ╤В╨╛ ╨┐╨╕╤И╨╡╤В | ╨Ъ╤В╨╛ ╤З╨╕╤В╨░╨╡╤В |
|--------|----------|-----------|------------|
| `source-documents` | ╨Ш╤Б╤Е╨╛╨┤╨╜╤Л╨╡ PDF/DOCX/PNG ╨╛╤В ╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╨╡╨╗╤П | Gateway | Document Service |
| `parsed-json` | ╨а╨░╤Б╨┐╨░╤А╤Б╨╡╨╜╨╜╤Л╨╣ ╤В╨╡╨║╤Б╤В ╨▓ JSON | Document Service | AI Service |
| `generated-json` | ╨б╨│╨╡╨╜╨╡╤А╨╕╤А╨╛╨▓╨░╨╜╨╜╨░╤П ╨╕╨╜╤Б╤В╤А╤Г╨║╤Ж╨╕╤П ╨▓ JSON | AI Service | Assembler Service |
| `result-documents` | ╨У╨╛╤В╨╛╨▓╤Л╨╣ PDF ╨┤╨╗╤П ╤Б╨║╨░╤З╨╕╨▓╨░╨╜╨╕╤П | Assembler Service | Gateway |

╨Т╤Б╨╡ 4 bucket'╨░ ╤Б╨╛╨╖╨┤╨░╤О╤В╤Б╤П ╨░╨▓╤В╨╛╨╝╨░╤В╨╕╤З╨╡╤Б╨║╨╕ ╨┐╤А╨╕ ╤Б╤В╨░╤А╤В╨╡ Gateway.

### ╨д╨╛╤А╨╝╨░╤В ╨║╨╗╤О╤З╨╡╨╣ (ObjectKey)

```
{bucket}/
  тФФтФАтФА {╨│╨╛╨┤}/
      тФФтФАтФА {╨╝╨╡╤Б╤П╤Ж}/
          тФФтФАтФА {taskId}/
              тФФтФАтФА {╤В╨╕╨┐}/
                  тФФтФАтФА {uuid}.{╤А╨░╤Б╤И╨╕╤А╨╡╨╜╨╕╨╡}
```

**╨Я╤А╨╕╨╝╨╡╤А╤Л:**
- `source-documents/2026/07/5de02bd9.../source/a1b2c3d4.pdf`
- `parsed-json/2026/07/5de02bd9.../parsed/e5f6g7h8.json`
- `generated-json/2026/07/5de02bd9.../generated/i9j0k1l2.json`
- `result-documents/2026/07/5de02bd9.../result/m3n4o5p6.pdf`

---

## ╨а╤Г╨║╨╛╨▓╨╛╨┤╤Б╤В╨▓╨╛ ╨┤╨╗╤П ╤Д╤А╨╛╨╜╤В╨╡╨╜╨┤-╤А╨░╨╖╤А╨░╨▒╨╛╤В╤З╨╕╨║╨░

### ╨Р╨▓╤В╨╛╤А╨╕╨╖╨░╤Ж╨╕╤П

╨Т╤Б╨╡ ╨╖╨░╨┐╤А╨╛╤Б╤Л ╨║ `/api/v1/tasks/**` ╤В╤А╨╡╨▒╤Г╤О╤В JWT-╤В╨╛╨║╨╡╨╜.

**╨а╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╤П:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"testuser@railway.com","password":"securePassword123","firstName":"Test","lastName":"User"}'
```

**╨Ы╨╛╨│╨╕╨╜:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"securePassword123"}'
```

╨Ю╤В╨▓╨╡╤В ╨╛╨▒╨╛╨╕╤Е ╨╖╨░╨┐╤А╨╛╤Б╨╛╨▓:
```json
{
  "accessToken": "eyJhbGciOiJIUzM4NCJ9...",
  "refreshToken": "...",
  "expiresIn": 900000,
  "tokenType": "Bearer"
}
```

### ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╨╜╨╕╨╡ ╤В╨╛╨║╨╡╨╜╨░

╨Т╤Б╨╡ ╨╖╨░╤Й╨╕╤Й╤С╨╜╨╜╤Л╨╡ ╨╖╨░╨┐╤А╨╛╤Б╤Л ╨┤╨╛╨╗╨╢╨╜╤Л ╤Б╨╛╨┤╨╡╤А╨╢╨░╤В╤М ╨╖╨░╨│╨╛╨╗╨╛╨▓╨╛╨║:
```
Authorization: Bearer <accessToken>
```

Access-╤В╨╛╨║╨╡╨╜ ╨╢╨╕╨▓╤С╤В **15 ╨╝╨╕╨╜╤Г╤В**. ╨Ъ╨╛╨│╨┤╨░ ╨╕╤Б╤В╨╡╨║╨░╨╡╤В тАФ ╨╛╨▒╨╜╨╛╨▓╨╕╤В╤М:
```bash
curl -X POST http://localhost:8080/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken":"<refreshToken>"}'
```

### ╨Ю╤Б╨╜╨╛╨▓╨╜╤Л╨╡ API-╤Н╨╜╨┤╨┐╨╛╨╕╨╜╤В╤Л

| ╨Ь╨╡╤В╨╛╨┤ | URL | ╨Ю╨┐╨╕╤Б╨░╨╜╨╕╨╡ |
|-------|-----|----------|
| `POST` | `/api/v1/tasks` | ╨Ч╨░╨│╤А╤Г╨╖╨╕╤В╤М ╨┤╨╛╨║╤Г╨╝╨╡╨╜╤В (multipart/form-data, ╨┐╨╛╨╗╨╡ `file`) |
| `GET` | `/api/v1/tasks` | ╨б╨┐╨╕╤Б╨╛╨║ ╨╖╨░╨┤╨░╤З (╨┐╨░╨│╨╕╨╜╨░╤Ж╨╕╤П, ╤Д╨╕╨╗╤М╤В╤А╨░╤Ж╨╕╤П) |
| `GET` | `/api/v1/tasks/{id}` | ╨Ф╨╡╤В╨░╨╗╨╕ ╨╖╨░╨┤╨░╤З╨╕ |
| `GET` | `/api/v1/tasks/{id}/status` | ╨в╨╛╨╗╤М╨║╨╛ ╤Б╤В╨░╤В╤Г╤Б ╨╖╨░╨┤╨░╤З╨╕ |
| `GET` | `/api/v1/tasks/{id}/download` | ╨б╨║╨░╤З╨░╤В╤М ╨│╨╛╤В╨╛╨▓╤Л╨╣ PDF |
| `DELETE` | `/api/v1/tasks/{id}` | ╨г╨┤╨░╨╗╨╕╤В╤М ╨╖╨░╨┤╨░╤З╤Г |

### ╨Я╨░╤А╨░╨╝╨╡╤В╤А╤Л ╨┤╨╗╤П GET /api/v1/tasks

| ╨Я╨░╤А╨░╨╝╨╡╤В╤А | ╨в╨╕╨┐ | ╨Я╨╛ ╤Г╨╝╨╛╨╗╤З╨░╨╜╨╕╤О | ╨Ю╨┐╨╕╤Б╨░╨╜╨╕╨╡ |
|----------|-----|-------------|----------|
| `page` | int | `0` | ╨Э╨╛╨╝╨╡╤А ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Л |
| `size` | int | `10` | ╨а╨░╨╖╨╝╨╡╤А ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Л |
| `sort` | string | `createdAt,desc` | ╨Я╨╛╨╗╨╡ ╨╕ ╨╜╨░╨┐╤А╨░╨▓╨╗╨╡╨╜╨╕╨╡ ╤Б╨╛╤А╤В╨╕╤А╨╛╨▓╨║╨╕ |
| `status` | string | тАФ | ╨д╨╕╨╗╤М╤В╤А: `CREATED`, `PARSING`, `PARSED`, `GENERATING`, `GENERATED`, `ASSEMBLING`, `COMPLETED`, `FAILED` |
| `createdFrom` | ISO 8601 | тАФ | ╨Ч╨░╨┤╨░╤З╨╕ ╤Б╨╛╨╖╨┤╨░╨╜╨╜╤Л╨╡ ╨┐╨╛╤Б╨╗╨╡ ╨┤╨░╤В╤Л |
| `createdTo` | ISO 8601 | тАФ | ╨Ч╨░╨┤╨░╤З╨╕ ╤Б╨╛╨╖╨┤╨░╨╜╨╜╤Л╨╡ ╨┤╨╛ ╨┤╨░╤В╤Л |

**╨Я╤А╨╕╨╝╨╡╤А:**
```
GET /api/v1/tasks?page=0&size=10&status=COMPLETED&sort=createdAt,desc&createdFrom=2026-07-01T00:00:00&createdTo=2026-07-31T23:59:59
```

### ╨б╤В╨░╤В╤Г╤Б╤Л ╨╖╨░╨┤╨░╤З╨╕

| ╨б╤В╨░╤В╤Г╤Б | ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ | resultAvailable |
|--------|----------|-----------------|
| `CREATED` | ╨Ч╨░╨┤╨░╤З╨░ ╤Б╨╛╨╖╨┤╨░╨╜╨░, ╤Д╨░╨╣╨╗ ╨╖╨░╨│╤А╤Г╨╢╨╡╨╜ | `false` |
| `PARSING` | Document Service ╨┐╨░╤А╤Б╨╕╤В ╨┤╨╛╨║╤Г╨╝╨╡╨╜╤В | `false` |
| `PARSED` | ╨Ф╨╛╨║╤Г╨╝╨╡╨╜╤В ╤А╨░╤Б╨┐╨░╤А╤Б╨╡╨╜ | `false` |
| `GENERATING` | AI Service ╨│╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В ╨╕╨╜╤Б╤В╤А╤Г╨║╤Ж╨╕╤О | `false` |
| `GENERATED` | ╨Ш╨╜╤Б╤В╤А╤Г╨║╤Ж╨╕╤П ╤Б╨│╨╡╨╜╨╡╤А╨╕╤А╨╛╨▓╨░╨╜╨░ | `false` |
| `ASSEMBLING` | Assembler Service ╤Б╨╛╨▒╨╕╤А╨░╨╡╤В PDF | `false` |
| `COMPLETED` | PDF ╨│╨╛╤В╨╛╨▓ ╨║ ╤Б╨║╨░╤З╨╕╨▓╨░╨╜╨╕╤О | **`true`** |
| `FAILED` | ╨Ю╤И╨╕╨▒╨║╨░ ╨╛╨▒╤А╨░╨▒╨╛╤В╨║╨╕ | `false` |

### Polling ╤Б╤В╨░╤В╤Г╤Б╨░

╨д╤А╨╛╨╜╤В╨╡╨╜╨┤ ╨┤╨╛╨╗╨╢╨╡╨╜ ╨╛╨┐╤А╨░╤И╨╕╨▓╨░╤В╤М `GET /api/v1/tasks/{id}/status` ╨║╨░╨╢╨┤╤Л╨╡ 2-3 ╤Б╨╡╨║╤Г╨╜╨┤╤Л, ╨┐╨╛╨║╨░:
- `status == "COMPLETED"` тЖТ ╨▓╤Л╨╖╨▓╨░╤В╤М `GET /api/v1/tasks/{id}/download`
- `status == "FAILED"` тЖТ ╨┐╨╛╨║╨░╨╖╨░╤В╤М `errorMessage`

╨Я╨╛╨╗╨╡ `resultAvailable` ╨▓ `TaskDetailsResponse` ╤Б╤В╨░╨╜╨╡╤В `true` ╤В╨╛╨╗╤М╨║╨╛ ╨║╨╛╨│╨┤╨░ ╤Б╤В╨░╤В╤Г╤Б = `COMPLETED`.

### Swagger

╨Я╨╛╨╗╨╜╨░╤П ╨┤╨╛╨║╤Г╨╝╨╡╨╜╤В╨░╤Ж╨╕╤П API ╤Б ╨▓╨╛╨╖╨╝╨╛╨╢╨╜╨╛╤Б╤В╤М╤О ╤В╨╡╤Б╤В╨╕╤А╨╛╨▓╨░╨╜╨╕╤П: http://localhost:8080/swagger-ui.html

**╨Ъ╨░╨║ ╨░╨▓╤В╨╛╤А╨╕╨╖╨╛╨▓╨░╤В╤М╤Б╤П ╨▓ Swagger:**
1. ╨Т╤Л╨┐╨╛╨╗╨╜╨╕ `POST /api/v1/auth/register` ╨╕╨╗╨╕ `POST /api/v1/auth/login`
2. ╨б╨║╨╛╨┐╨╕╤А╤Г╨╣ `accessToken` ╨╕╨╖ ╨╛╤В╨▓╨╡╤В╨░
3. ╨Э╨░╨╢╨╝╨╕ ╨║╨╜╨╛╨┐╨║╤Г **Authorize** (╨╖╨░╨╝╨╛╨║ ╤Б╨┐╤А╨░╨▓╨░ ╨▓╨▓╨╡╤А╤Е╤Г)
4. ╨Т╤Б╤В╨░╨▓╤М: `Bearer <accessToken>`
5. ╨Э╨░╨╢╨╝╨╕ **Authorize** тЖТ **Close**

---

## ╨б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╤П ╤А╨░╨▒╨╛╤В╤Л ╨╝╨╕╨║╤А╨╛╤Б╨╡╤А╨▓╨╕╤Б╨╛╨▓ (╤А╤Г╤З╨╜╨░╤П ╨╛╤В╨╗╨░╨┤╨║╨░ ╨┐╨╛╨╗╨╜╨╛╨│╨╛ ╤Ж╨╕╨║╨╗╨░)

╨Я╤А╨╡╨┤╨┐╨╛╨╗╨╛╨╢╨╕╨╝ ╤З╤В╨╛ Document Service, AI Service ╨╕ Assembler Service ╨╡╤Й╤С ╨╜╨╡ ╨│╨╛╤В╨╛╨▓╤Л, ╨╝╨╛╨╢╨╜╨╛ ╨▓╤А╤Г╤З╨╜╤Г╤О ╨┐╤А╨╛╨▓╨╡╤Б╤В╨╕ ╨╖╨░╨┤╨░╤З╤Г ╤З╨╡╤А╨╡╨╖ ╨▓╨╡╤Б╤М ╨╢╨╕╨╖╨╜╨╡╨╜╨╜╤Л╨╣ ╤Ж╨╕╨║╨╗, ╨┐╤Г╨▒╨╗╨╕╨║╤Г╤П ╤Б╨╛╨▒╤Л╤В╨╕╤П ╨▓ RabbitMQ Management ╨┤╨╗╤П ╨╜╨░╨│╨╗╤П╨┤╨╜╨╛╤Б╤В╨╕.

### ╨и╨░╨│ 1: ╨Я╨╛╨╗╤Г╤З╨╕╤В╤М taskId

╨б╨╛╨╖╨┤╨░╨╣ ╨╖╨░╨┤╨░╤З╤Г ╤З╨╡╤А╨╡╨╖ Swagger (`POST /api/v1/tasks`) ╨╕ ╤Б╨║╨╛╨┐╨╕╤А╤Г╨╣ `id` ╨╕╨╖ ╨╛╤В╨▓╨╡╤В╨░.

**╨Я╤А╨╕╨╝╨╡╤А:** `5de02bd9-9663-4bc3-bd41-9383bf925b32`

### ╨и╨░╨│ 2: ╨Ю╤В╨┐╤А╨░╨▓╨╕╤В╤М ╤Б╨╛╨▒╤Л╤В╨╕╤П ╨┐╨╛ ╨┐╨╛╤А╤П╨┤╨║╤Г

╨Ю╤В╨║╤А╨╛╨╣ http://localhost:15672 тЖТ ╨▓╨║╨╗╨░╨┤╨║╨░ **Exchanges** тЖТ `task.exchange` тЖТ **Publish Message**

**Routing key ╨┤╨╗╤П ╨▓╤Б╨╡╤Е ╤Б╨╛╨▒╤Л╤В╨╕╨╣:** `task.status`

**╨Я╨╛╨┤╤Б╤В╨░╨▓╤М ╤Б╨▓╨╛╨╣ taskId** ╨▓╨╛ ╨▓╤Б╨╡ `taskId`, `correlationId` ╨╕ ╨┐╤Г╤В╨╕ `ObjectKey`.

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `PARSING`

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `PARSED`

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `GENERATING`

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `GENERATED`

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `ASSEMBLING`

### ╨и╨░╨│ 3: ╨Ч╨░╨│╤А╤Г╨╖╨╕╤В╤М ╤В╨╡╤Б╤В╨╛╨▓╤Л╨╣ PDF ╨▓ MinIO

╨Я╨╡╤А╨╡╨┤ ╨╛╤В╨┐╤А╨░╨▓╨║╨╛╨╣ `COMPLETED` ╨╜╤Г╨╢╨╜╨╛ ╨▓╤А╤Г╤З╨╜╤Г╤О ╨╖╨░╨│╤А╤Г╨╖╨╕╤В╤М PDF ╨▓ MinIO:

1. ╨Ю╤В╨║╤А╨╛╨╣ http://localhost:9001 тЖТ `minioadmin` / `minioadmin`
2. ╨Т╨╛╨╣╨┤╨╕ ╨▓ bucket **result-documents**
3. ╨Э╨░╨╢╨╝╨╕ **Upload** тЖТ ╨▓╤Л╨▒╨╡╤А╨╕ ╨╗╤О╨▒╨╛╨╣ PDF-╤Д╨░╨╣╨╗ ╤Б ╨║╨╛╨╝╨┐╤М╤О╤В╨╡╤А╨░
4. ╨Я╨╛╤Б╨╗╨╡ ╨╖╨░╨│╤А╤Г╨╖╨║╨╕ ╨╜╨░╨╢╨╝╨╕ ╨╜╨░ ╤Д╨░╨╣╨╗ ╨┐╤А╨░╨▓╨╛╨╣ ╨║╨╜╨╛╨┐╨║╨╛╨╣ тЖТ **Rename**
5. ╨Т╤Б╤В╨░╨▓╤М ╨┐╤Г╤В╤М: `2026/07/5de02bd9-9663-4bc3-bd41-9383bf925b32/result/test.pdf`

### ╨и╨░╨│ 4: ╨Ю╤В╨┐╤А╨░╨▓╨╕╤В╤М COMPLETED

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `COMPLETED`

### ╨и╨░╨│ 5: ╨б╨║╨░╤З╨░╤В╤М ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В

`GET /api/v1/tasks/5de02bd9-9663-4bc3-bd41-9383bf925b32/download` тЖТ ╤Б╨║╨░╤З╨░╨╡╤В╤Б╤П PDF

### ╨С╨╛╨╜╤Г╤Б: FAILED (╤Б╨╕╨╝╤Г╨╗╤П╤Ж╨╕╤П ╨╛╤И╨╕╨▒╨║╨╕)

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
**╨Я╤А╨╛╨▓╨╡╤А╨║╨░:** ╤Б╤В╨░╤В╤Г╤Б тЖТ `FAILED`, `GET /api/v1/tasks/{id}/download` тЖТ 409

---

## ╨Я╤А╨╛╤Б╨╝╨╛╤В╤А ╨╗╨╛╨│╨╛╨▓ Gateway

```powershell
# ╨Т╤Б╨╡ ╨╗╨╛╨│╨╕
docker logs railway-gateway

# ╨Ы╨╛╨│╨╕ ╨▓ ╤А╨╡╨░╨╗╤М╨╜╨╛╨╝ ╨▓╤А╨╡╨╝╨╡╨╜╨╕ (Ctrl+C ╤З╤В╨╛╨▒╤Л ╨▓╤Л╨╣╤В╨╕)
docker logs -f railway-gateway

# ╨Я╨╛╤Б╨╗╨╡╨┤╨╜╨╕╨╡ 100 ╤Б╤В╤А╨╛╨║
docker logs --tail 100 railway-gateway
```

**╨Ъ╨╗╤О╤З╨╡╨▓╤Л╨╡ ╤Б╤В╤А╨╛╨║╨╕ ╨▓ ╨╗╨╛╨│╨░╤Е:**

| ╨б╤В╤А╨╛╨║╨░ | ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ |
|--------|----------|
| `Task created successfully: taskId=...` | ╨Ч╨░╨┤╨░╤З╨░ ╤Б╨╛╨╖╨┤╨░╨╜╨░ |
| `Publishing event: type=TASK_CREATED` | ╨б╨╛╨▒╤Л╤В╨╕╨╡ ╨╛╤В╨┐╤А╨░╨▓╨╗╨╡╨╜╨╛ ╨▓ RabbitMQ |
| `Received event: type=PARSING_STARTED` | Gateway ╨┐╨╛╨╗╤Г╤З╨╕╨╗ ╤Б╨╛╨▒╤Л╤В╨╕╨╡ |
| `Task status updated: oldStatus=..., newStatus=...` | ╨б╤В╨░╤В╤Г╤Б ╨╕╨╖╨╝╨╡╨╜╨╕╨╗╤Б╤П |
| `Task not found for ... event: taskId=...` | ╨б╨╛╨▒╤Л╤В╨╕╨╡ ╨┤╨╗╤П ╨╜╨╡╤Б╤Г╤Й╨╡╤Б╤В╨▓╤Г╤О╤Й╨╡╨╣ ╨╖╨░╨┤╨░╤З╨╕ тАФ ╨┐╤А╨╛╨▓╨╡╤А╤М taskId |

---

## ╨Ч╨░╨┐╤Г╤Б╨║ ╤В╨╡╤Б╤В╨╛╨▓

```powershell
# ╨Т╤Б╨╡ ╤В╨╡╤Б╤В╤Л
mvn test -pl gateway -am

# ╨Ъ╨╛╨╜╨║╤А╨╡╤В╨╜╤Л╨╣ ╤В╨╡╤Б╤В╨╛╨▓╤Л╨╣ ╨║╨╗╨░╤Б╤Б
mvn test -pl gateway -am -Dtest=AuthControllerIntegrationTest

# ╨Ъ╨╛╨╜╨║╤А╨╡╤В╨╜╤Л╨╣ ╨╝╨╡╤В╨╛╨┤
mvn test -pl gateway -am -Dtest=AuthControllerIntegrationTest#shouldRegisterUserSuccessfully
```

**╨в╤А╨╡╨▒╨╛╨▓╨░╨╜╨╕╨╡:** Docker ╨┤╨╛╨╗╨╢╨╡╨╜ ╨▒╤Л╤В╤М ╨╖╨░╨┐╤Г╤Й╨╡╨╜ (Testcontainers ╨┐╨╛╨┤╨╜╨╕╨╝╨░╨╡╤В ╨║╨╛╨╜╤В╨╡╨╣╨╜╨╡╤А╤Л ╨░╨▓╤В╨╛╨╝╨░╤В╨╕╤З╨╡╤Б╨║╨╕).

### ╨б╨▓╨╛╨┤╨║╨░ ╨┐╨╛ ╤В╨╡╤Б╤В╨░╨╝ (41 ╤Б╤Ж╨╡╨╜╨░╤А╨╕╨╣)

| ╨в╨╡╤Б╤В╨╛╨▓╤Л╨╣ ╨║╨╗╨░╤Б╤Б | ╨б╤Ж╨╡╨╜╨░╤А╨╕╨╡╨▓ | ╨з╤В╨╛ ╨┐╤А╨╛╨▓╨╡╤А╤П╨╡╤В |
|----------------|-----------|---------------|
| `AuthControllerIntegrationTest` | 8 | ╨а╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╤П, ╨┤╤Г╨▒╨╗╨╕╨║╨░╤В╤Л, ╨╗╨╛╨│╨╕╨╜, ╨╜╨╡╨▓╨╡╤А╨╜╤Л╨╣ ╨┐╨░╤А╨╛╨╗╤М, refresh, revoked refresh, logout |
| `TaskControllerIntegrationTest` | 20 | ╨б╨╛╨╖╨┤╨░╨╜╨╕╨╡, ╨▓╨░╨╗╨╕╨┤╨░╤Ж╨╕╤П, ╨┤╨╡╤В╨░╨╗╨╕, ╤Б╤В╨░╤В╤Г╤Б, ╤Б╨┐╨╕╤Б╨╛╨║, ╤Д╨╕╨╗╤М╤В╤А╨░╤Ж╨╕╤П, ╨┐╨░╨│╨╕╨╜╨░╤Ж╨╕╤П, ╤З╤Г╨╢╨░╤П ╨╖╨░╨┤╨░╤З╨░, ╤Г╨┤╨░╨╗╨╡╨╜╨╕╨╡, ╤Б╨║╨░╤З╨╕╨▓╨░╨╜╨╕╨╡, 401 ╨▒╨╡╨╖ JWT |
| `RabbitEventPublisherIntegrationTest` | 3 | ╨Я╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╤П, ╤Б╨╡╤А╨╕╨░╨╗╨╕╨╖╨░╤Ж╨╕╤П, routing key |
| `RabbitEventListenerIntegrationTest` | 6 | 5 ╤В╨╕╨┐╨╛╨▓ ╤Б╨╛╨▒╤Л╤В╨╕╨╣ + ╨╖╨░╨┤╨░╤З╨░ ╨╜╨╡ ╨╜╨░╨╣╨┤╨╡╨╜╨░ |
| `MinioServiceImplIntegrationTest` | 7 | Upload, download, delete, exists, copy, metadata |

---

## ╨б╤В╤А╤Г╨║╤В╤Г╤А╨░ ╨┐╤А╨╛╨╡╨║╤В╨░

```
railway-gateway/
тФЬтФАтФА pom.xml                          # ╨а╨╛╨┤╨╕╤В╨╡╨╗╤М╤Б╨║╨╕╨╣ POM
тФЬтФАтФА docker-compose.dev.yml           # Docker Compose ╨┤╨╗╤П ╤А╨░╨╖╤А╨░╨▒╨╛╤В╨║╨╕
тФЬтФАтФА Dockerfile                       # ╨б╨▒╨╛╤А╨║╨░ ╨╛╨▒╤А╨░╨╖╨░ Gateway
тФЬтФАтФА .gitignore
тФЬтФАтФА .dockerignore
тФЬтФАтФА README.md
тФФтФАтФА gateway/
    тФЬтФАтФА pom.xml                      # POM ╨╝╨╛╨┤╤Г╨╗╤П Gateway
    тФФтФАтФА src/
        тФЬтФАтФА main/
        тФВ   тФЬтФАтФА java/com/railway/gateway/
        тФВ   тФВ   тФЬтФАтФА GatewayApplication.java
        тФВ   тФВ   тФЬтФАтФА api/              # ╨Ъ╨╛╨╜╤В╤А╨╛╨╗╨╗╨╡╤А╤Л ╨╕ DTO
        тФВ   тФВ   тФВ   тФЬтФАтФА controller/
        тФВ   тФВ   тФВ   тФВ   тФЬтФАтФА AuthController.java
        тФВ   тФВ   тФВ   тФВ   тФФтФАтФА TaskController.java
        тФВ   тФВ   тФВ   тФФтФАтФА dto/          # Records: Request/Response DTO
        тФВ   тФВ   тФЬтФАтФА application/      # Use cases, ╨╝╨░╨┐╨┐╨╡╤А╤Л, ╨▓╨░╨╗╨╕╨┤╨░╤В╨╛╤А╤Л
        тФВ   тФВ   тФВ   тФЬтФАтФА mapper/
        тФВ   тФВ   тФВ   тФЬтФАтФА service/
        тФВ   тФВ   тФВ   тФФтФАтФА validator/
        тФВ   тФВ   тФЬтФАтФА domain/           # ╨С╨╕╨╖╨╜╨╡╤Б-╨╗╨╛╨│╨╕╨║╨░ (╤Б╤Г╤Й╨╜╨╛╤Б╤В╨╕, enums, ╨╕╤Б╨║╨╗╤О╤З╨╡╨╜╨╕╤П, ╨╕╨╜╤В╨╡╤А╤Д╨╡╨╣╤Б╤Л)
        тФВ   тФВ   тФВ   тФЬтФАтФА entity/
        тФВ   тФВ   тФВ   тФЬтФАтФА enums/
        тФВ   тФВ   тФВ   тФЬтФАтФА event/
        тФВ   тФВ   тФВ   тФЬтФАтФА exception/
        тФВ   тФВ   тФВ   тФЬтФАтФА repository/
        тФВ   тФВ   тФВ   тФЬтФАтФА service/      # ╨Ш╨╜╤В╨╡╤А╤Д╨╡╨╣╤Б╤Л (EventPublisher, MinioService)
        тФВ   тФВ   тФВ   тФФтФАтФА valueobject/
        тФВ   тФВ   тФФтФАтФА infrastructure/   # ╨а╨╡╨░╨╗╨╕╨╖╨░╤Ж╨╕╨╕ (JPA, MinIO, RabbitMQ, Security)
        тФВ   тФВ       тФЬтФАтФА config/
        тФВ   тФВ       тФЬтФАтФА properties/
        тФВ   тФВ       тФЬтФАтФА repository/
        тФВ   тФВ       тФЬтФАтФА security/
        тФВ   тФВ       тФФтФАтФА service/
        тФВ   тФФтФАтФА resources/
        тФВ       тФЬтФАтФА application.yml
        тФВ       тФЬтФАтФА application-dev.yml
        тФВ       тФФтФАтФА db/migration/     # Flyway ╨╝╨╕╨│╤А╨░╤Ж╨╕╨╕
        тФФтФАтФА test/                     # ╨Ш╨╜╤В╨╡╨│╤А╨░╤Ж╨╕╨╛╨╜╨╜╤Л╨╡ ╤В╨╡╤Б╤В╤Л
```

---

## ╨Я╨╛╨╗╨╡╨╖╨╜╤Л╨╡ ╨║╨╛╨╝╨░╨╜╨┤╤Л

```powershell
# ╨в╨╛╨╗╤М╨║╨╛ ╤Б╨╛╨▒╤А╨░╤В╤М, ╨▒╨╡╨╖ ╤В╨╡╤Б╤В╨╛╨▓
mvn clean package -DskipTests -pl gateway -am

# ╨Ч╨░╨┐╤Г╤Б╤В╨╕╤В╤М ╨▓╤Б╨╡ ╤В╨╡╤Б╤В╤Л
mvn test -pl gateway -am

# ╨Я╨╛╤Б╨╝╨╛╤В╤А╨╡╤В╤М ╨┤╨╡╤А╨╡╨▓╨╛ ╨╖╨░╨▓╨╕╤Б╨╕╨╝╨╛╤Б╤В╨╡╨╣
mvn dependency:tree -pl gateway

# ╨Ч╨░╨┐╤Г╤Б╤В╨╕╤В╤М Gateway ╨╗╨╛╨║╨░╨╗╤М╨╜╨╛ (╨▒╨╡╨╖ Docker, ╨╕╨╜╤Д╤А╨░╤Б╤В╤А╤Г╨║╤В╤Г╤А╨░ ╨┤╨╛╨╗╨╢╨╜╨░ ╨▒╤Л╤В╤М ╨╖╨░╨┐╤Г╤Й╨╡╨╜╨░ ╨╛╤В╨┤╨╡╨╗╤М╨╜╨╛)
mvn spring-boot:run -pl gateway -am -Dspring-boot.run.profiles=dev
```
