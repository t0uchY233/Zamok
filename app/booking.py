from flask import jsonify, request
from app import app, db
from app.database import Booking, Apartment, User
from datetime import datetime, timedelta
import random
import string
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def update_google_sheet(booking_data):
    """Обновление Google Sheet с информацией о бронировании"""
    try:
        app.logger.info(f"Начинаем обновление Google Sheet для бронирования {booking_data['booking_id']}")
        
        # Форматируем даты
        check_in = datetime.fromisoformat(booking_data['check_in_date']).strftime("%d.%m.%Y %H:%M")
        check_out = datetime.fromisoformat(booking_data['check_out_date']).strftime("%d.%m.%Y %H:%M")
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        credentials_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.getenv('GOOGLE_CREDENTIALS_FILE') + '.json')
        app.logger.info(f"Используем файл учетных данных: {credentials_file}")
        
        if not os.path.exists(credentials_file):
            app.logger.error(f"Файл учетных данных не найден: {credentials_file}")
            raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        
        if not spreadsheet_id:
            app.logger.error("SPREADSHEET_ID не настроен")
            raise ValueError("SPREADSHEET_ID not configured")
        
        app.logger.info(f"Используем таблицу: {spreadsheet_id}")
        
        # Подготовка данных для записи
        values = [[
            booking_data['booking_id'],
            booking_data['user_name'],
            booking_data['apartment_title'],
            check_in,
            check_out,
            booking_data['total_price'],
            booking_data['status'],
            current_time
        ]]
        
        body = {
            'values': values
        }
        
        app.logger.info(f"Подготовленные данные: {values}")
        
        # Сначала получим информацию о листах
        sheets_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheets_metadata.get('sheets', '')
        sheet_title = sheets[0]['properties']['title']  # Берем название первого листа
        
        app.logger.info(f"Название первого листа: {sheet_title}")
        
        # Запись данных в таблицу
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_title}'!A:H",  # Используем полученное название листа
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        app.logger.info(f"Данные успешно записаны в таблицу: {result}")
        return True
        
    except Exception as e:
        app.logger.error(f"Ошибка при обновлении Google Sheet: {str(e)}")
        app.logger.exception(e)
        raise

@app.route('/api/bookings/check-availability', methods=['POST'])
def check_availability():
    """Проверка доступности квартиры на указанные даты"""
    data = request.json
    apartment_id = data['apartment_id']
    check_in = datetime.fromisoformat(data['check_in_date'])
    check_out = datetime.fromisoformat(data['check_out_date'])
    
    # Проверяем существующие бронирования
    conflicting_bookings = Booking.query.filter(
        Booking.apartment_id == apartment_id,
        Booking.status != 'cancelled',
        Booking.check_in_date < check_out,
        Booking.check_out_date > check_in
    ).all()
    
    if conflicting_bookings:
        return jsonify({
            'status': 'error',
            'available': False,
            'message': 'Apartment is not available for selected dates'
        }), 400
    
    # Рассчитываем стоимость
    apartment = Apartment.query.get_or_404(apartment_id)
    days = (check_out - check_in).days
    total_price = days * apartment.price_per_day
    
    return jsonify({
        'status': 'success',
        'available': True,
        'total_price': total_price,
        'days': days
    })

@app.route('/api/bookings/create', methods=['POST'])
def create_booking():
    """Создание нового бронирования"""
    try:
        data = request.json
        
        # Валидация обязательных полей
        required_fields = ['user_id', 'apartment_id', 'check_in_date', 'check_out_date', 'total_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Проверка пользователя
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        if not user.is_verified:
            return jsonify({
                'status': 'error',
                'message': 'User is not verified. Please complete verification process.'
            }), 403
        
        # Проверка квартиры
        apartment = Apartment.query.get(data['apartment_id'])
        if not apartment:
            return jsonify({
                'status': 'error',
                'message': 'Apartment not found'
            }), 404
            
        if not apartment.is_available:
            return jsonify({
                'status': 'error',
                'message': 'Apartment is not available for booking'
            }), 400
        
        # Проверяем корректность дат
        try:
            check_in = datetime.fromisoformat(data['check_in_date'])
            check_out = datetime.fromisoformat(data['check_out_date'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
            }), 400
            
        if check_in >= check_out:
            return jsonify({
                'status': 'error',
                'message': 'Check-out date must be after check-in date'
            }), 400
            
        if check_in < datetime.now():
            return jsonify({
                'status': 'error',
                'message': 'Check-in date cannot be in the past'
            }), 400
        
        # Проверка доступности дат
        conflicting_bookings = Booking.query.filter(
            Booking.apartment_id == data['apartment_id'],
            Booking.status != 'cancelled',
            Booking.check_in_date < check_out,
            Booking.check_out_date > check_in
        ).all()
        
        if conflicting_bookings:
            return jsonify({
                'status': 'error',
                'message': 'Apartment is not available for selected dates'
            }), 400
        
        # Проверка корректности стоимости
        days = (check_out - check_in).days
        expected_price = days * apartment.price_per_day
        
        if abs(float(data['total_price']) - expected_price) > 0.01:  # Допустимая погрешность
            return jsonify({
                'status': 'error',
                'message': f'Price calculation mismatch. Expected: {expected_price}'
            }), 400
        
        # Создаем бронирование
        booking = Booking(
            user_id=data['user_id'],
            apartment_id=data['apartment_id'],
            check_in_date=check_in,
            check_out_date=check_out,
            total_price=data['total_price'],
            # Генерируем уникальный код доступа для умного замка
            access_code=''.join(random.choices(string.digits, k=6))
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Обновляем Google Sheet
        booking_data = {
            'booking_id': booking.id,
            'user_name': user.full_name,
            'apartment_title': apartment.title,
            'check_in_date': data['check_in_date'],
            'check_out_date': data['check_out_date'],
            'total_price': data['total_price'],
            'status': 'pending'
        }
        
        try:
            update_google_sheet(booking_data)
        except Exception as sheet_error:
            app.logger.error(f"Ошибка при обновлении Google Sheet: {str(sheet_error)}")
            # Не отменяем бронирование при ошибке с Google Sheet
        
        return jsonify({
            'status': 'success',
            'booking_id': booking.id,
            'access_code': booking.access_code,
            'message': 'Booking created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка при создании бронирования: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Отмена бронирования"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status == 'confirmed' and booking.is_paid:
        return jsonify({
            'status': 'error',
            'message': 'Cannot cancel paid booking'
        }), 400
    
    booking.status = 'cancelled'
    db.session.commit()
    
    # Обновляем Google Sheet
    user = User.query.get(booking.user_id)
    apartment = Apartment.query.get(booking.apartment_id)
    booking_data = {
        'booking_id': booking.id,
        'user_name': user.full_name,
        'apartment_title': apartment.title,
        'check_in_date': booking.check_in_date.isoformat(),
        'check_out_date': booking.check_out_date.isoformat(),
        'total_price': booking.total_price,
        'status': 'cancelled'
    }
    update_google_sheet(booking_data)
    
    return jsonify({
        'status': 'success',
        'message': 'Booking cancelled successfully'
    }) 