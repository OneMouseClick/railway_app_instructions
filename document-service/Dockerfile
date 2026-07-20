# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV LIBREOFFICE_PATH=/usr/bin/soffice
ENV TMPDIR=/tmp

# Устанавливаем LibreOffice
RUN apt-get update && apt-get install -y \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-common \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Проверяем, что LibreOffice установлен
RUN which soffice && soffice --version || echo "LibreOffice not found"

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Создаем директории для временных файлов
RUN mkdir -p /tmp/tp_uploads /tmp/tp_convert

# Открываем порт
EXPOSE 8000

# Команда для запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]