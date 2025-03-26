from flask import jsonify, request, render_template, send_from_directory
from app import app, db
from app.database import User, Apartment, Booking, Payment, Owner
from datetime import datetime
import random
import string
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apartments')
def apartments_page():
    return render_template('index.html')

@app.route('/owner')
def owner_page():
    return send_from_directory(os.path.join(app.root_path, '..', 'frontend'), 'owner.html')

@app.route('/default-apartment.jpg')
def default_apartment():
    try:
        return send_from_directory(os.path.join(app.root_path, '..', 'frontend', 'static', 'images'), 'default-apartment.jpg')
    except Exception as e:
        app.logger.error(f"Error serving default image: {str(e)}")
        return "Image not found", 404

@app.route('/favicon.ico')
def favicon():
    # Исправляем путь к favicon.ico
    favicon_path = os.path.join(app.root_path, '..', 'frontend')
    app.logger.info(f"Путь к favicon: {favicon_path}")
    app.logger.info(f"Файл существует: {os.path.exists(os.path.join(favicon_path, 'favicon.ico'))}")
    
    return send_from_directory(favicon_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow()})

@app.route('/api/apartments', methods=['GET'])
def get_apartments():
    try:
        apartments = Apartment.query.filter_by(is_available=True).all()
        apartments_list = []
        
        app.logger.info(f"Найдено квартир: {len(apartments)}")
        
        for apt in apartments:
            apartment_data = {
                'id': apt.id,
                'title': apt.title,
                'address': apt.address,
                'description': apt.description,
                'price_per_day': apt.price_per_day,
                'image_url': apt.image_url
            }
            apartments_list.append(apartment_data)
            app.logger.info(f"Добавлена квартира: {apartment_data}")
        
        app.logger.info(f"Отправляем ответ: {apartments_list}")
        return jsonify(apartments_list)
    except Exception as e:
        app.logger.error(f"Ошибка в get_apartments: {str(e)}")
        app.logger.error(f"Тип ошибки: {type(e)}")
        return jsonify({'error': str(e)}), 500

# Маршруты для хозяев
@app.route('/api/owners/register', methods=['POST'])
def register_owner():
    """Регистрация нового хозяина"""
    try:
        data = request.json
        
        # Проверяем, существует ли уже хозяин с таким telegram_id
        existing_owner = Owner.query.filter_by(telegram_id=data['telegram_id']).first()
        if existing_owner:
            return jsonify({
                'status': 'error',
                'message': 'Owner with this Telegram ID already exists'
            }), 400
        
        # Создаем нового хозяина
        owner = Owner(
            telegram_id=data['telegram_id'],
            username=data.get('username', ''),
            full_name=data.get('full_name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            is_verified=False
        )
        
        db.session.add(owner)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'owner_id': owner.id,
            'message': 'Owner registered successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка при регистрации хозяина: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/owners/<int:telegram_id>', methods=['GET'])
def get_owner(telegram_id):
    """Получение информации о хозяине по telegram_id"""
    owner = Owner.query.filter_by(telegram_id=telegram_id).first()
    
    if not owner:
        return jsonify({
            'status': 'error',
            'message': 'Owner not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'owner': {
            'id': owner.id,
            'telegram_id': owner.telegram_id,
            'username': owner.username,
            'full_name': owner.full_name,
            'phone': owner.phone,
            'email': owner.email,
            'is_verified': owner.is_verified,
            'registration_date': owner.registration_date.isoformat()
        }
    })

@app.route('/api/owners/<int:owner_id>/apartments', methods=['GET'])
def get_owner_apartments(owner_id):
    """Получение списка квартир хозяина"""
    owner = Owner.query.get_or_404(owner_id)
    
    apartments = []
    for apt in owner.apartments:
        apartments.append({
            'id': apt.id,
            'title': apt.title,
            'address': apt.address,
            'description': apt.description,
            'price_per_day': apt.price_per_day,
            'is_available': apt.is_available,
            'image_url': apt.image_url
        })
    
    return jsonify({
        'status': 'success',
        'apartments': apartments
    })

@app.route('/api/owners/apartments/create', methods=['POST'])
def create_apartment():
    """Создание новой квартиры хозяином"""
    try:
        data = request.json
        
        # Проверяем, существует ли хозяин
        owner = Owner.query.get_or_404(data['owner_id'])
        
        # Создаем новую квартиру
        apartment = Apartment(
            title=data['title'],
            address=data['address'],
            description=data['description'],
            price_per_day=data['price_per_day'],
            is_available=data.get('is_available', True),
            smart_lock_id=data.get('smart_lock_id', ''),
            image_url=data.get('image_url', ''),
            owner_id=owner.id
        )
        
        db.session.add(apartment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'apartment_id': apartment.id,
            'message': 'Apartment created successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка при создании квартиры: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/owners/apartments/<int:apartment_id>', methods=['PUT'])
def update_apartment(apartment_id):
    """Обновление информации о квартире"""
    try:
        apartment = Apartment.query.get_or_404(apartment_id)
        data = request.json
        
        # Проверяем, принадлежит ли квартира хозяину
        if data.get('owner_id') and apartment.owner_id != data['owner_id']:
            return jsonify({
                'status': 'error',
                'message': 'You do not have permission to update this apartment'
            }), 403
        
        # Обновляем данные квартиры
        if 'title' in data:
            apartment.title = data['title']
        if 'address' in data:
            apartment.address = data['address']
        if 'description' in data:
            apartment.description = data['description']
        if 'price_per_day' in data:
            apartment.price_per_day = data['price_per_day']
        if 'is_available' in data:
            apartment.is_available = data['is_available']
        if 'smart_lock_id' in data:
            apartment.smart_lock_id = data['smart_lock_id']
        if 'image_url' in data:
            apartment.image_url = data['image_url']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Apartment updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/owners/<int:owner_id>/bookings', methods=['GET'])
def get_owner_bookings(owner_id):
    """Получение списка бронирований для квартир хозяина"""
    owner = Owner.query.get_or_404(owner_id)
    
    # Получаем все квартиры хозяина
    apartments = owner.apartments
    
    # Собираем все бронирования для этих квартир
    bookings = []
    for apt in apartments:
        for booking in apt.bookings:
            user = User.query.get(booking.user_id)
            bookings.append({
                'id': booking.id,
                'apartment_title': apt.title,
                'user_name': user.full_name,
                'check_in_date': booking.check_in_date.isoformat(),
                'check_out_date': booking.check_out_date.isoformat(),
                'total_price': booking.total_price,
                'status': booking.status,
                'is_paid': booking.is_paid,
                'created_at': booking.created_at.isoformat()
            })
    
    return jsonify({
        'status': 'success',
        'bookings': bookings
    })

@app.route('/api/access-code/<int:booking_id>', methods=['POST'])
def generate_access_code(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if not booking.is_paid:
        return jsonify({'status': 'error', 'message': 'Booking is not paid'}), 400
    
    # Генерация 6-значного кода
    access_code = ''.join(random.choices(string.digits, k=6))
    booking.access_code = access_code
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'access_code': access_code,
        'valid_until': booking.check_out_date
    })

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    data = request.json
    booking = Booking.query.get_or_404(data['booking_id'])
    
    payment = Payment(
        booking_id=booking.id,
        amount=data['amount'],
        payment_method=data['payment_method'],
        transaction_id=data['transaction_id']
    )
    
    booking.is_paid = True
    booking.status = 'confirmed'
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Payment verified'}) 