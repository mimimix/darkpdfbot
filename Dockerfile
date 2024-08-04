# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y \
    libmagic1 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . .

# Команда для запуска скрипта
CMD ["python", "main.py"]
