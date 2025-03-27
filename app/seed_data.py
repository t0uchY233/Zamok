import os
import logging
from datetime import datetime, timedelta
from app import get_db_connection, init_db
from app.database import User, Owner, Apartment, Booking

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """Заполнение базы данных тестовыми данными"""
    try:
        # Инициализация базы данных (создание таблиц)
        init_db()
        logger.info("База данных инициализирована")
        
        # Создаем пользователей
        user_id1 = User.create(
            username="Иван Иванов",
            email="ivan@example.com",
            password_hash="pbkdf2:sha256:150000$abcdef$123456789abcdef"
        )
        
        user_id2 = User.create(
            username="Мария Петрова",
            email="maria@example.com",
            password_hash="pbkdf2:sha256:150000$abcdef$123456789abcdef"
        )
        
        user_id3 = User.create(
            username="Алексей Сидоров",
            email="alex@example.com",
            password_hash="pbkdf2:sha256:150000$abcdef$123456789abcdef"
        )
        
        logger.info(f"Создано пользователей: 3 (ID: {user_id1}, {user_id2}, {user_id3})")
        
        # Создаем хозяев квартир
        owner_id1 = Owner.create(
            telegram_id="123456789",
            username="landlord1",
            full_name="Сергей Владимирович",
            phone="+7 (999) 123-45-67",
            email="sergey@example.com",
            is_verified=True
        )
        
        owner_id2 = Owner.create(
            telegram_id="987654321",
            username="landlord2",
            full_name="Елена Михайловна",
            phone="+7 (999) 765-43-21",
            email="elena@example.com",
            is_verified=True
        )
        
        logger.info(f"Создано хозяев: 2 (ID: {owner_id1}, {owner_id2})")
        
        # Создаем квартиры
        apartment_id1 = Apartment.create(
            title="Уютная студия в центре",
            address="ул. Ленина, 10",
            description="Светлая студия с прекрасным видом на центр города",
            price_per_day=2500,
            image_url="/static/images/apartment1.jpg",
            owner_id=owner_id1,
            smart_lock_id="SL12345",
            is_available=True
        )
        
        apartment_id2 = Apartment.create(
            title="Двухкомнатная квартира рядом с парком",
            address="ул. Пушкина, 25",
            description="Просторная двухкомнатная квартира рядом с парком",
            price_per_day=3500,
            image_url="/static/images/apartment2.jpg",
            owner_id=owner_id1,
            smart_lock_id="SL12346",
            is_available=True
        )
        
        apartment_id3 = Apartment.create(
            title="Люкс-апартаменты с джакузи",
            address="ул. Гагарина, 15",
            description="Элитные апартаменты с джакузи и панорамными окнами",
            price_per_day=5000,
            image_url="/static/images/apartment3.jpg",
            owner_id=owner_id2,
            smart_lock_id="SL12347",
            is_available=True
        )
        
        logger.info(f"Создано квартир: 3 (ID: {apartment_id1}, {apartment_id2}, {apartment_id3})")
        
        # Создаем бронирования
        today = datetime.now().date()
        
        booking_id1 = Booking.create(
            user_id=user_id1,
            apartment_id=apartment_id1,
            check_in_date=(today + timedelta(days=5)).strftime('%Y-%m-%d'),
            check_out_date=(today + timedelta(days=8)).strftime('%Y-%m-%d'),
            total_price=7500,
            status='confirmed'
        )
        
        booking_id2 = Booking.create(
            user_id=user_id2,
            apartment_id=apartment_id2,
            check_in_date=(today + timedelta(days=10)).strftime('%Y-%m-%d'),
            check_out_date=(today + timedelta(days=15)).strftime('%Y-%m-%d'),
            total_price=17500,
            status='pending'
        )
        
        booking_id3 = Booking.create(
            user_id=user_id3,
            apartment_id=apartment_id3,
            check_in_date=(today + timedelta(days=7)).strftime('%Y-%m-%d'),
            check_out_date=(today + timedelta(days=10)).strftime('%Y-%m-%d'),
            total_price=15000,
            status='confirmed'
        )
        
        logger.info(f"Создано бронирований: 3 (ID: {booking_id1}, {booking_id2}, {booking_id3})")
        
        logger.info("База данных успешно заполнена тестовыми данными!")
        return True
    except Exception as e:
        logger.error(f"Ошибка при заполнении базы данных: {str(e)}")
        return False

if __name__ == "__main__":
    seed_database() 