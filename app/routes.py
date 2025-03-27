import os
import json
import logging
from datetime import datetime
from flask import render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from app import app
import random

# Включаем CORS
CORS(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Тестовые данные
APARTMENTS = [
    {
        "id": 1,
        "title": "Уютная квартира в центре",
        "address": "ул. Ленина, 10",
        "price_per_day": 2500,
        "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-4.0.3",  # Используем реальное изображение
        "description": "Светлая квартира с современным ремонтом",
        "has_wifi": True,
        "has_kitchen": True,
        "has_parking": False,
        "has_smart_lock": True
    }
]

@app.route('/')
def index():
    """Главная страница"""
    return app.send_static_file('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Обработка статических файлов"""
    return send_from_directory(app.static_folder, filename)

@app.route('/get-quote')
def get_quote():
    """Страница для расчета и оформления бронирования"""
    # Вместо рендеринга шаблона, будем использовать статический HTML файл
    # Так он будет использовать интеграцию с Telegram Mini App как в index.html
    return app.send_static_file('get_quote.html')

@app.route('/api/calculate-price', methods=['POST'])
def calculate_price():
    """API для расчета стоимости бронирования"""
    try:
        data = request.json
        logger.info(f"Received price calculation request: {data}")
        
        apartment_id = data.get('apartment_id')
        check_in_date = datetime.strptime(data.get('check_in_date'), '%Y-%m-%d')
        check_out_date = datetime.strptime(data.get('check_out_date'), '%Y-%m-%d')
        
        # Находим нужную квартиру из тестовых данных
        apartments = {
            '1': {'price_per_day': 2500},
            '2': {'price_per_day': 3500},
            '3': {'price_per_day': 5000}
        }
        
        apartment = apartments.get(apartment_id)
        
        if not apartment:
            return jsonify({'error': 'Apartment not found'}), 404
        
        # Рассчитываем количество дней
        num_days = (check_out_date - check_in_date).days
        
        if num_days <= 0:
            return jsonify({'error': 'Check-out date must be after check-in date'}), 400
        
        # Рассчитываем стоимость
        price_per_day = apartment['price_per_day']
        total_price = price_per_day * num_days
        
        return jsonify({
            'apartment_id': apartment_id,
            'check_in_date': check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': check_out_date.strftime('%Y-%m-%d'),
            'num_days': num_days,
            'price_per_day': price_per_day,
            'total_price': total_price
        })
    except Exception as e:
        logger.error(f"Error calculating price: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-quote', methods=['POST'])
def submit_quote():
    try:
        # Получаем данные из запроса
        data = request.json
        app.logger.info(f"Получены данные бронирования: {data}")
        
        if not data:
            return jsonify({"error": "Данные не получены"}), 400
        
        # Проверяем наличие необходимых полей
        required_fields = ['apartment_id', 'dates', 'total_price', 'user_info']
        for field in required_fields:
            if field not in data:
                app.logger.error(f"Отсутствует обязательное поле: {field}")
                return jsonify({"error": f"Отсутствует обязательное поле: {field}"}), 400
        
        # Извлекаем данные
        apartment_id = data.get('apartment_id')
        dates = data.get('dates', {})
        user_info = data.get('user_info', {})
        total_price = data.get('total_price')
        
        # Проверяем даты
        if 'check_in_date' not in dates or 'check_out_date' not in dates:
            app.logger.error("Отсутствуют даты заезда/выезда")
            return jsonify({"error": "Отсутствуют даты заезда/выезда"}), 400
        
        app.logger.info(f"Даты бронирования: {dates}")
        app.logger.info(f"Общая стоимость: {total_price}")
        
        # Генерируем уникальный ID бронирования
        booking_id = random.randint(10000, 99999)
        
        # Преобразуем ID апартаментов в название
        apartment_names = {
            1: "Квартира на Ленина",
            2: "Квартира на Гагарина",
            3: "Квартира в центре"
        }
        
        apartment_name = apartment_names.get(apartment_id, f"Квартира #{apartment_id}")
        
        # Формируем данные для записи
        booking_data = {
            'booking_id': booking_id,
            'name': f"{user_info.get('name', 'Гость')} {user_info.get('phone', '')}",
            'apartment_id': apartment_id,
            'apartment_name': apartment_name,
            'check_in_date': dates.get('check_in_date'),
            'check_out_date': dates.get('check_out_date'),
            'total_price': total_price,
            'status': 'новое'
        }
        
        app.logger.info(f"Подготовлены данные для записи в базу: {booking_data}")
        
        try:
            # Импортируем функцию для работы с Airtable
            from app.airtable_integration import add_booking_to_airtable
            
            # Добавляем данные в Airtable
            result = add_booking_to_airtable(booking_data)
            
            if result:
                app.logger.info(f"Бронирование №{booking_id} успешно создано и сохранено в Airtable")
                return jsonify({
                    "success": True,
                    "booking_id": booking_id,
                    "message": "Бронирование успешно создано"
                })
            else:
                app.logger.error("Ошибка при записи данных в Airtable")
                return jsonify({
                    "success": False,
                    "error": "Ошибка при создании бронирования (проблема с сохранением данных)"
                }), 500
        except Exception as e:
            app.logger.error(f"Исключение при работе с Airtable: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({
                "success": False,
                "error": "Ошибка при создании бронирования (проблема с сохранением данных)"
            }), 500
            
    except Exception as e:
        app.logger.error(f"Ошибка при создании бронирования: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/default-apartment.jpg')
def default_apartment():
    return app.send_static_file('images/default-apartment.jpg')

@app.route('/api/apartments', methods=['GET'])
def get_apartments():
    """API для получения списка доступных квартир"""
    try:
        logger.info("Получен запрос на список квартир")
        return jsonify(APARTMENTS)
    except Exception as e:
        logger.error(f"Error getting apartments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('images/favicon.ico')

@app.route('/api/bookings/create', methods=['POST'])
def create_booking():
    """API для создания нового бронирования"""
    try:
        data = request.json
        logger.info(f"Received booking creation request: {data}")
        
        # Проверяем, что данные вообще пришли
        if not data:
            logger.error("No JSON data received")
            return jsonify({'success': False, 'error': 'Нет данных для бронирования'}), 400
        
        # Проверяем наличие всех необходимых полей и логируем каждое поле
        required_fields = ['apartment_id', 'check_in_date', 'check_out_date', 'total_price']
        missing_fields = []
        
        # Подробное логирование каждого поля
        for field in required_fields:
            field_value = data.get(field)
            logger.info(f"Field {field}: {field_value}")
            
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
            logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Генерируем ID бронирования
        booking_id = 12345  # В реальной БД будет автоинкремент
        
        # Поиск названия апартаментов по ID
        apartment_names = {
            '1': 'Уютная студия в центре',
            '2': 'Апартаменты с видом',
            '3': 'Люкс-апартаменты'
        }
        
        apartment_name = apartment_names.get(str(data['apartment_id']), 'Неизвестные апартаменты')
        
        # Получаем имя пользователя из данных Telegram или используем "Пользователь Telegram"
        user_name = data.get('user_name', 'Пользователь Telegram')
        user_phone = data.get('phone', '')  # Может отсутствовать при бронировании из основной страницы
        
        # Собираем полный набор данных для записи
        booking_data = {
            'booking_id': booking_id,
            'name': user_name,
            'phone': user_phone,
            'email': data.get('email', ''),
            'apartment_id': data['apartment_id'],
            'apartment_name': apartment_name,
            'check_in_date': data['check_in_date'],
            'check_out_date': data['check_out_date'],
            'total_price': data['total_price'],
            'status': 'pending'
        }
        
        # Логируем данные перед отправкой
        logger.info(f"Подготовлены данные для записи в базу: {booking_data}")
        
        # Импортируем функцию для работы с Airtable
        from app.airtable_integration import add_booking_to_airtable
        
        # Отправляем данные в Airtable
        airtable_result = add_booking_to_airtable(booking_data)
        
        if not airtable_result:
            logger.warning("Данные не были сохранены в Airtable, но бронирование создано")
        
        return jsonify({
            'success': True,
            'booking_id': booking_id
        })
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test-env')
def test_env():
    """Тестовый маршрут для проверки переменных окружения"""
    try:
        env_data = {
            "AIRTABLE_API_KEY": os.environ.get("AIRTABLE_API_KEY", "не задан")[-5:] if os.environ.get("AIRTABLE_API_KEY") else "не задан",
            "AIRTABLE_BASE_ID": os.environ.get("AIRTABLE_BASE_ID", "не задан"),
            "AIRTABLE_TABLE_NAME": os.environ.get("AIRTABLE_TABLE_NAME", "не задан"),
        }
        app.logger.info(f"Переменные окружения: {env_data}")
        return jsonify(env_data)
    except Exception as e:
        app.logger.error(f"Ошибка при проверке переменных окружения: {e}")
        return jsonify({"error": str(e)}), 500 