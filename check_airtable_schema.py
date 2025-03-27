import os
import requests
import json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем конфигурацию из переменных окружения
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

print(f"AIRTABLE_API_KEY: {'*' * 5}{AIRTABLE_API_KEY[-5:] if AIRTABLE_API_KEY else 'не задан'}")
print(f"AIRTABLE_BASE_ID: {AIRTABLE_BASE_ID or 'не задан'}")
print(f"AIRTABLE_TABLE_NAME: {AIRTABLE_TABLE_NAME or 'не задан'}")

# Формируем URL для запроса метаданных таблицы
url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"

# Заголовки запроса
headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

try:
    # Выполняем GET-запрос к Airtable API для получения метаданных
    response = requests.get(url, headers=headers)
    
    # Выводим информацию о ответе
    print(f"Статус ответа: {response.status_code}")
    
    # Если запрос успешен, выводим структуру таблицы
    if response.status_code == 200:
        data = response.json()
        
        # Ищем нашу таблицу в списке
        for table in data.get("tables", []):
            if table.get("name") == AIRTABLE_TABLE_NAME:
                print(f"\nТаблица найдена: {table.get('name')}")
                print("\nПоля таблицы:")
                
                # Выводим информацию о полях
                for field in table.get("fields", []):
                    print(f"- {field.get('name')} (тип: {field.get('type')})")
                
                break
        else:
            print(f"Таблица '{AIRTABLE_TABLE_NAME}' не найдена в базе")
    else:
        print(f"Ошибка при запросе метаданных: {response.text}")
except Exception as e:
    print(f"Ошибка при выполнении запроса: {e}") 