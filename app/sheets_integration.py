import os
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# ID таблицы, напрямую задаем, если возникают проблемы с загрузкой из .env
SPREADSHEET_ID = "1w-htQLLMfZlzB9rjwW8eP0Up50dcg5D56peKbLgJDWk"
SHEET_NAME = "Лист1"  # Имя листа в таблице

# Настройка логирования
logger = logging.getLogger(__name__)

def get_google_sheets_client():
    """Получение клиента для работы с Google Sheets"""
    try:
        # Путь к файлу с учетными данными сервисного аккаунта
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'quick-flame-437017-e6-53c51b17c354.json')
        
        logger.info(f"Попытка найти файл с учетными данными: {credentials_file}")
        
        # Проверяем наличие файла в текущей директории
        if os.path.exists(credentials_file):
            credentials_path = credentials_file
        else:
            # Ищем файл в корне проекта
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            credentials_path = os.path.join(base_path, credentials_file)
        
        logger.info(f"Используем путь к файлу учетных данных: {credentials_path}")
        
        if not os.path.exists(credentials_path):
            logger.error(f"Файл с учетными данными не найден: {credentials_path}")
            return None
        
        # Определяем области доступа
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']
        
        # Современный метод аутентификации
        credentials = Credentials.from_service_account_file(
            credentials_path, 
            scopes=scope
        )
        
        # Создаем клиент
        client = gspread.authorize(credentials)
        
        logger.info("Успешно создан клиент Google Sheets")
        
        return client
    except Exception as e:
        logger.error(f"Ошибка при подключении к Google Sheets: {str(e)}")
        return None

def add_booking_to_sheet(booking_data):
    """Добавляет данные о бронировании в Google Sheets"""
    try:
        # Подключаемся к Google Sheets
        client = get_google_sheets_client()
        if not client:
            logger.error("Не удалось подключиться к Google Sheets")
            return False
        
        logger.info(f"Открываем таблицу с ID: {SPREADSHEET_ID}")
        
        try:
            # Открываем таблицу по ID
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            
            # Получаем лист по имени или используем первый лист
            try:
                sheet = spreadsheet.worksheet(SHEET_NAME)
                logger.info(f"Найден лист: {SHEET_NAME}")
            except gspread.exceptions.WorksheetNotFound:
                sheet = spreadsheet.sheet1
                logger.info("Лист по имени не найден, используем первый лист")
                
        except Exception as e:
            logger.error(f"Ошибка при открытии таблицы: {str(e)}")
            return False
        
        # Получаем текущую дату и время для записи
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Форматируем даты в читаемый формат
        check_in_date = booking_data.get('check_in_date', '')
        check_out_date = booking_data.get('check_out_date', '')
        
        # Форматируем строковые данные
        booking_id = str(booking_data.get('booking_id', ''))
        name = str(booking_data.get('name', 'Тестовый пользователь'))
        apartment_name = str(booking_data.get('apartment_name', 'Квартира'))
        status = str(booking_data.get('status', 'pending'))
        
        # Форматируем цену
        total_price = booking_data.get('total_price', 0)
        formatted_price = f"{total_price:,.2f}".replace(",", " ").replace(".00", "")
        
        # Формируем данные для записи в соответствии с колонками в таблице
        row_data = [
            booking_id,                 # ID бронирования
            name,                       # Имя клиента
            apartment_name,             # Название апартаментов
            check_in_date,              # Дата заезда
            check_out_date,             # Дата выезда
            formatted_price,            # Общая стоимость
            status,                     # Статус бронирования
            current_time                # Временная метка создания записи
        ]
        
        logger.info(f"Данные для записи в таблицу: {row_data}")
        
        # Добавляем данные в таблицу
        sheet.append_row(row_data)
        logger.info("Данные успешно записаны в Google Sheets")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении данных в Google Sheets: {str(e)}")
        return False 