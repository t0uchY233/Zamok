from flask import jsonify, request
from app import app, db
from app.database import User, Apartment, Booking, Payment
from datetime import datetime
import random
import string

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow()})

@app.route('/api/apartments', methods=['GET'])
def get_apartments():
    apartments = Apartment.query.filter_by(is_available=True).all()
    return jsonify([{
        'id': apt.id,
        'title': apt.title,
        'address': apt.address,
        'price_per_day': apt.price_per_day,
        'description': apt.description
    } for apt in apartments])

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    try:
        booking = Booking(
            user_id=data['user_id'],
            apartment_id=data['apartment_id'],
            check_in_date=datetime.fromisoformat(data['check_in_date']),
            check_out_date=datetime.fromisoformat(data['check_out_date']),
            total_price=data['total_price']
        )
        db.session.add(booking)
        db.session.commit()
        return jsonify({'status': 'success', 'booking_id': booking.id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

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