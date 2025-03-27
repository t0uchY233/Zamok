FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя без прав root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Создаем необходимые директории с правильными правами
RUN mkdir -p /app/instance

# Открываем порты
EXPOSE 5000

# Запускаем приложение
CMD ["python", "run_all.py"] 