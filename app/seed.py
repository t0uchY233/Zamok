from app import app, db
from app.database import Apartment

def seed_data():
    # Список тестовых квартир
    apartments = [
        {
            'title': 'Уютная студия в центре',
            'address': 'ул. Ленина, 15',
            'description': 'Современная студия с панорамными окнами и новым ремонтом. Есть все необходимое для комфортного проживания.',
            'price_per_day': 2500.0,
            'is_available': True,
            'smart_lock_id': 'LOCK001',
            'image_url': 'https://example.com/images/apartment1.jpg'
        },
        {
            'title': 'Двухкомнатная квартира с видом на парк',
            'address': 'пр. Мира, 42',
            'description': 'Просторная квартира в тихом районе. Две раздельные комнаты, большая кухня, свежий ремонт.',
            'price_per_day': 3500.0,
            'is_available': True,
            'smart_lock_id': 'LOCK002',
            'image_url': 'https://example.com/images/apartment2.jpg'
        },
        {
            'title': 'Люкс апартаменты в бизнес-центре',
            'address': 'ул. Пушкина, 7',
            'description': 'Премиум квартира с дизайнерским ремонтом. Полностью укомплектована техникой, есть джакузи.',
            'price_per_day': 5000.0,
            'is_available': True,
            'smart_lock_id': 'LOCK003',
            'image_url': 'https://example.com/images/apartment3.jpg'
        }
    ]
    
    try:
        # Удаляем существующие записи
        Apartment.query.delete()
        
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