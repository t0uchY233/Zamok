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
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_CREDENTIALS_FILE'),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID not configured")
        
        # Подготовка данных для записи
        values = [[
            booking_data['booking_id'],
            booking_data['user_name'],
            booking_data['apartment_title'],
            booking_data['check_in_date'],
            booking_data['check_out_date'],
            booking_data['total_price'],
            booking_data['status'],
            datetime.now().isoformat()
        ]]
        
        body = {
            'values': values
        }
        
        # Запись данных в таблицу
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Bookings!A:H',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False

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
    data = request.json
    user = User.query.get_or_404(data['user_id'])
    
    if not user.is_verified:
        return jsonify({
            'status': 'error',
            'message': 'User is not verified'
        }), 403
    
    try:
        # Создаем бронирование
        booking = Booking(
            user_id=data['user_id'],
            apartment_id=data['apartment_id'],
            check_in_date=datetime.fromisoformat(data['check_in_date']),
            check_out_date=datetime.fromisoformat(data['check_out_date']),
            total_price=data['total_price']
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Обновляем Google Sheet
        apartment = Apartment.query.get(data['apartment_id'])
        booking_data = {
            'booking_id': booking.id,
            'user_name': user.full_name,
            'apartment_title': apartment.title,
            'check_in_date': data['check_in_date'],
            'check_out_date': data['check_out_date'],
            'total_price': data['total_price'],
            'status': 'pending'
        }
        update_google_sheet(booking_data)
        
        return jsonify({
            'status': 'success',
            'booking_id': booking.id,
            'message': 'Booking created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
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