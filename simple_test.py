import requests
import json

# URL запроса
url = 'http://127.0.0.1:5000/api/test-env'

# Отправляем GET запрос для проверки переменных окружения
response = requests.get(url)
print(f"Проверка переменных окружения: {response.text}")

# Создаем очень простой запрос бронирования
simple_data = {
    "apartment_id": 1,
    "dates": {
        "check_in_date": "2025-04-10",
        "check_out_date": "2025-04-15"
    },
    "total_price": 12500,
    "user_info": {
        "name": "Тест",
        "phone": "123"
    }
}

# Отправляем POST запрос
headers = {'Content-Type': 'application/json'}
response = requests.post('http://127.0.0.1:5000/api/submit-quote', json=simple_data, headers=headers)

# Выводим результат
print(f"Статус код: {response.status_code}")
print(f"Ответ: {response.text}") 