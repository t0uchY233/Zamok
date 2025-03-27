import os
import requests
from datetime import datetime
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем конфигурацию из переменных окружения
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

# Выводим значения переменных окружения для отладки
logger.info(f"AIRTABLE_API_KEY: {'*' * 5}{AIRTABLE_API_KEY[-5:] if AIRTABLE_API_KEY else 'не задан'}")
logger.info(f"AIRTABLE_BASE_ID: {AIRTABLE_BASE_ID or 'не задан'}")
logger.info(f"AIRTABLE_TABLE_NAME: {AIRTABLE_TABLE_NAME or 'не задан'}")

def test_airtable_api():
    try:
        # Формируем тестовые данные бронирования
        booking_data = {
            "booking_id": 12345,
            "name": "Тестовый Пользователь",
            "phone": "+7 999 123 4567",
            "email": "test@example.com",
            "apartment_name": "Квартира на Ленина",
            "check_in_date": "2025-04-10",
            "check_out_date": "2025-04-15",
            "total_price": 12500,
            "status": "новое"
        }
        
        # Формируем URL и заголовки
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Подготавливаем данные полей - используем только простые поля
        fields = {
            "ID бронирования": booking_data.get("booking_id"),
            "Дата заезда": booking_data.get("check_in_date"),
            "Дата выезда": booking_data.get("check_out_date"),
            "Стоимость": booking_data.get("total_price"),
            "Временная метка создания записи": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        
        payload = {"fields": fields}
        logger.info(f"URL для запроса: {url}")
        logger.info(f"Заголовки: {headers}")
        logger.info(f"Отправка данных в Airtable: {payload}")
        
        # Отправляем запрос
        response = requests.post(url, json=payload, headers=headers)
        
        # Логируем ответ
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Ответ от Airtable: {response.text}")
        
        # Проверяем успешность
        if response.status_code == 200:
            logger.info("Тест успешно пройден! Запись добавлена в Airtable.")
            return True
        else:
            logger.error(f"Тест не пройден. Код ответа: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при тестировании Airtable API: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_airtable_api() 