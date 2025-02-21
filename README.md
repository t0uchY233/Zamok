# Zamok - MVP платформа для аренды квартир

## Описание проекта
Zamok - это минималистичная платформа для аренды квартир с упрощенной аутентификацией через Telegram. Проект разработан как MVP для быстрого тестирования основных сценариев работы сервиса аренды жилья.

## Основные функции
- Упрощённая аутентификация через загрузку документов
- Бронирование квартир через Telegram бот
- Система генерации временных кодов доступа
- Интеграция с Google Sheets для администрирования

## Установка и запуск

### Предварительные требования
- Python 3.8+
- Telegram Bot Token
- Google Cloud Project credentials
- SQLite (опционально)

### Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/zamok.git
cd zamok
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env и добавьте необходимые переменные окружения:
```
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_CREDENTIALS_FILE=path_to_credentials.json
```

### Запуск
1. Запустите Flask сервер:
```bash
python run.py
```

2. Запустите Telegram бот:
```bash
python bot/bot.py
```

## Структура проекта
```
/project_root
├── /app                    # Flask приложение
├── /bot                    # Telegram бот
├── /frontend              # Telegram Mini App
├── /docs                  # Документация
└── requirements.txt       # Зависимости проекта
```

## Разработка
- Backend: Python/Flask
- База данных: SQLite/JSON
- Интерфейс: Telegram Bot + Mini App

## Лицензия
MIT 