import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем конфигурацию из переменных окружения
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

# Проверка наличия параметров
if not AIRTABLE_API_KEY:
    logging.error("Отсутствует AIRTABLE_API_KEY в переменных окружения")
if not AIRTABLE_BASE_ID:
    logging.error("Отсутствует AIRTABLE_BASE_ID в переменных окружения")
if not AIRTABLE_TABLE_NAME:
    logging.error("Отсутствует AIRTABLE_TABLE_NAME в переменных окружения")

logger = logging.getLogger(__name__)

def add_booking_to_airtable(booking_data):
    """Добавляет данные о бронировании в Airtable."""
    try:
        # Полное логирование входных данных
        logger.info(f"Получены данные для сохранения в Airtable: {booking_data}")
        
        # Выводим значения переменных окружения для отладки
        logger.info(f"AIRTABLE_API_KEY: {'*' * 5}{AIRTABLE_API_KEY[-5:] if AIRTABLE_API_KEY else 'не задан'}")
        logger.info(f"AIRTABLE_BASE_ID: {AIRTABLE_BASE_ID or 'не задан'}")
        logger.info(f"AIRTABLE_TABLE_NAME: {AIRTABLE_TABLE_NAME or 'не задан'}")
        
        # Формируем заголовки и URL для запроса
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Получаем текущую дату и время для записи, если нет в booking_data
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Преобразуем ID бронирования в число, если это строка
        booking_id = booking_data.get("booking_id")
        if isinstance(booking_id, str) and booking_id.isdigit():
            booking_id = int(booking_id)
        
        # Подготавливаем данные полей бронирования для отправки в Airtable
        # Сначала добавляем только простые поля (текст и числа)
        fields = {
            "ID бронирования": booking_id,
            "Дата заезда": booking_data.get("check_in_date"),
            "Дата выезда": booking_data.get("check_out_date"),
            "Стоимость": booking_data.get("total_price"),
            "Временная метка создания записи": booking_data.get("current_time", current_time)
        }
        
        # Добавляем поля выбора только если они совпадают с предопределенными значениями
        # (в реальном приложении можно реализовать проверку допустимых значений)
        if booking_data.get("name"):
            fields["Имя пользователя"] = booking_data.get("name")
            
        if booking_data.get("apartment_name"):
            fields["Название квартиры"] = booking_data.get("apartment_name")
            
        if booking_data.get("status"):
            fields["Статус"] = booking_data.get("status")
        
        payload = {"fields": fields}
        logger.info(f"URL для запроса: {url}")
        logger.info(f"Отправка данных бронирования в Airtable: {fields}")
        
        # Выполняем POST-запрос к Airtable API
        response = requests.post(url, json=payload, headers=headers)
        
        # Логируем ответ от Airtable API
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Ответ от Airtable: {response.text}")
        
        response.raise_for_status()  # выбросит исключение при ошибке HTTP
        
        logger.info("Данные успешно записаны в Airtable")
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении данных в Airtable: {e}")
        # Выводим полную информацию об исключении для отладки
        import traceback
        logger.error(traceback.format_exc())
        return False 