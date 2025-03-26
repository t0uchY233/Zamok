import requests
import json
from datetime import datetime, timedelta

def create_test_booking():
    # URL нашего API
    url = 'http://localhost:5000/api/bookings/create'
    
    # Данные для бронирования
    booking_data = {
        'user_id': 1,
        'apartment_id': 1,
        'check_in_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'check_out_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'total_price': 5000
    }
    
    # Отправляем POST запрос
    try:
        response = requests.post(url, json=booking_data)
        print(f'Статус ответа: {response.status_code}')
        print(f'Ответ: {response.json()}')
        
        # Если бронирование успешно создано, подтверждаем оплату
        if response.status_code == 200:
            booking_id = response.json().get('booking_id')
            if booking_id:
                payment_url = 'http://localhost:5000/api/verify-payment'
                payment_data = {
                    'booking_id': booking_id,
                    'amount': 5000,
                    'payment_method': 'test',
                    'transaction_id': 'test_transaction_123'
                }
                
                payment_response = requests.post(payment_url, json=payment_data)
                print(f'Статус подтверждения оплаты: {payment_response.status_code}')
                print(f'Ответ подтверждения оплаты: {payment_response.json()}')
    
    except Exception as e:
        print(f'Ошибка при создании бронирования: {e}')

if __name__ == '__main__':
    create_test_booking() 