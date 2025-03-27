import requests
import json

# URL запроса
url = 'http://127.0.0.1:5000/api/submit-quote'

# Данные для тестового бронирования
data = {
    "apartment_id": 1,
    "dates": {
        "check_in_date": "2025-04-10",
        "check_out_date": "2025-04-15"
    },
    "total_price": 12500,
    "user_info": {
        "name": "Тестовый Пользователь",
        "phone": "+7 999 123 4567"
    }
}

# Отправляем POST запрос
headers = {'Content-Type': 'application/json'}
response = requests.post(url, json=data, headers=headers)

# Выводим результат
print(f"Статус код: {response.status_code}")
print(f"Ответ: {response.text}")

# Проверяем успешность запроса
if response.status_code == 200:
    result = response.json()
    if result.get('success'):
        print(f"Бронирование успешно создано с ID: {result.get('booking_id')}")
    else:
        print(f"Ошибка при создании бронирования: {result.get('error')}")
else:
    print(f"Ошибка HTTP: {response.status_code}") 