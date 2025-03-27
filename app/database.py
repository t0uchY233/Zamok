import sqlite3
from datetime import datetime

def get_db_connection():
    """Получить соединение с базой данных SQLite"""
    from app import get_db_connection as app_get_db_connection
    return app_get_db_connection()

class User:
    """Класс для работы с пользователями"""
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_by_telegram_id(telegram_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def create(username, email=None, password_hash=None, telegram_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, telegram_id) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, telegram_id)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    @staticmethod
    def update(user_id, **kwargs):
        if not kwargs:
            return False
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(user_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return users

class Owner:
    """Класс для работы с хозяевами квартир"""
    
    @staticmethod
    def get_by_id(owner_id):
        conn = get_db_connection()
        owner = conn.execute('SELECT * FROM owners WHERE id = ?', (owner_id,)).fetchone()
        conn.close()
        return owner
    
    @staticmethod
    def get_by_telegram_id(telegram_id):
        conn = get_db_connection()
        owner = conn.execute('SELECT * FROM owners WHERE telegram_id = ?', (telegram_id,)).fetchone()
        conn.close()
        return owner
    
    @staticmethod
    def create(telegram_id, username=None, full_name=None, phone=None, email=None, is_verified=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO owners (telegram_id, username, full_name, phone, email, is_verified) VALUES (?, ?, ?, ?, ?, ?)',
            (telegram_id, username, full_name, phone, email, is_verified)
        )
        conn.commit()
        owner_id = cursor.lastrowid
        conn.close()
        return owner_id
    
    @staticmethod
    def update(owner_id, **kwargs):
        if not kwargs:
            return False
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(owner_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE owners SET {set_clause} WHERE id = ?', params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        owners = conn.execute('SELECT * FROM owners').fetchall()
        conn.close()
        return owners

class Apartment:
    """Класс для работы с квартирами"""
    
    @staticmethod
    def get_by_id(apartment_id):
        conn = get_db_connection()
        apartment = conn.execute('SELECT * FROM apartments WHERE id = ?', (apartment_id,)).fetchone()
        conn.close()
        return apartment
    
    @staticmethod
    def create(title, address, price_per_day, description=None, image_url=None, owner_id=None, smart_lock_id=None, is_available=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO apartments (title, address, description, price_per_day, image_url, owner_id, smart_lock_id, is_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (title, address, description, price_per_day, image_url, owner_id, smart_lock_id, is_available)
        )
        conn.commit()
        apartment_id = cursor.lastrowid
        conn.close()
        return apartment_id
    
    @staticmethod
    def update(apartment_id, **kwargs):
        if not kwargs:
            return False
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(apartment_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE apartments SET {set_clause} WHERE id = ?', params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    @staticmethod
    def get_all(available_only=True, owner_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM apartments'
        params = []
        
        conditions = []
        if available_only:
            conditions.append('is_available = ?')
            params.append(True)
        
        if owner_id:
            conditions.append('owner_id = ?')
            params.append(owner_id)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        apartments = cursor.execute(query, params).fetchall()
        conn.close()
        return apartments
    
    @staticmethod
    def delete(apartment_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM apartments WHERE id = ?', (apartment_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

class Booking:
    """Класс для работы с бронированиями"""
    
    @staticmethod
    def get_by_id(booking_id):
        conn = get_db_connection()
        booking = conn.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
        conn.close()
        return booking
    
    @staticmethod
    def create(user_id, apartment_id, check_in_date, check_out_date, total_price, status='pending'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bookings (user_id, apartment_id, check_in_date, check_out_date, total_price, status) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, apartment_id, check_in_date, check_out_date, total_price, status)
        )
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return booking_id
    
    @staticmethod
    def update_status(booking_id, status):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, booking_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    @staticmethod
    def get_bookings_for_apartment(apartment_id, active_only=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM bookings WHERE apartment_id = ?'
        params = [apartment_id]
        
        if active_only:
            query += ' AND status != ?'
            params.append('cancelled')
        
        bookings = cursor.execute(query, params).fetchall()
        conn.close()
        return bookings
    
    @staticmethod
    def get_user_bookings(user_id):
        conn = get_db_connection()
        bookings = conn.execute('SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
        conn.close()
        return bookings
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        bookings = conn.execute('SELECT * FROM bookings').fetchall()
        conn.close()
        return bookings

class Payment:
    """Класс для работы с платежами"""
    
    @staticmethod
    def get_by_id(payment_id):
        conn = get_db_connection()
        payment = conn.execute('SELECT * FROM payments WHERE id = ?', (payment_id,)).fetchone()
        conn.close()
        return payment
    
    @staticmethod
    def create(booking_id, amount, payment_method, transaction_id=None, status='pending'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO payments (booking_id, amount, payment_method, transaction_id, status) VALUES (?, ?, ?, ?, ?)',
            (booking_id, amount, payment_method, transaction_id, status)
        )
        conn.commit()
        payment_id = cursor.lastrowid
        conn.close()
        return payment_id
    
    @staticmethod
    def update_status(payment_id, status):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE payments SET status = ? WHERE id = ?', (status, payment_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    @staticmethod
    def get_by_booking_id(booking_id):
        conn = get_db_connection()
        payments = conn.execute('SELECT * FROM payments WHERE booking_id = ?', (booking_id,)).fetchall()
        conn.close()
        return payments 