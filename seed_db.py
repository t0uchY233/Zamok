from app import app, db
from app.database import Apartment, User, Owner

def seed_data():
    try:
        # Создаем тестового пользователя
        test_user = User(
            telegram_id=123456789,
            username="test_user",
            full_name="Test User",
            is_verified=True
        )
        db.session.add(test_user)
        db.session.commit()
        print('Тестовый пользователь создан')
        
        # Создаем тестового хозяина
        test_owner = Owner(
            telegram_id=987654321,
            username="test_owner",
            full_name="Владелец Квартиры",
            phone="+7 (999) 123-45-67",
            email="owner@example.com",
            is_verified=True
        )
        db.session.add(test_owner)
        db.session.commit()
        print('Тестовый хозяин создан')
        
        # Список тестовых квартир
        apartments = [
            {
                'title': 'Уютная студия в центре',
                'address': 'ул. Ленина, 15',
                'description': 'Современная студия с панорамными окнами и новым ремонтом. Есть все необходимое для комфортного проживания.',
                'price_per_day': 2500.0,
                'is_available': True,
                'smart_lock_id': 'LOCK001',
                'image_url': '/static/images/apartments/apartment1.jpg',
                'owner_id': test_owner.id
            },
            {
                'title': 'Двухкомнатная квартира с видом на парк',
                'address': 'пр. Мира, 42',
                'description': 'Просторная квартира в тихом районе. Две раздельные комнаты, большая кухня, свежий ремонт.',
                'price_per_day': 3500.0,
                'is_available': True,
                'smart_lock_id': 'LOCK002',
                'image_url': '/static/images/apartments/apartment2.jpg',
                'owner_id': test_owner.id
            },
            {
                'title': 'Люкс апартаменты в бизнес-центре',
                'address': 'ул. Пушкина, 7',
                'description': 'Премиум квартира с дизайнерским ремонтом. Полностью укомплектована техникой, есть джакузи.',
                'price_per_day': 5000.0,
                'is_available': True,
                'smart_lock_id': 'LOCK003',
                'image_url': '/static/images/apartments/apartment3.jpg',
                'owner_id': test_owner.id
            }
        ]
        
        # Добавляем новые квартиры
        for apt_data in apartments:
            apartment = Apartment(**apt_data)
            db.session.add(apartment)
        
        db.session.commit()
        print('Тестовые данные успешно добавлены')
    except Exception as e:
        print(f'Ошибка при добавлении данных: {e}')
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        seed_data() 