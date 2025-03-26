from app import app, db
from app.database import Apartment

def check_apartments():
    with app.app_context():
        apartments = Apartment.query.all()
        print(f"Всего квартир: {len(apartments)}")
        for apt in apartments:
            print(f"ID: {apt.id}")
            print(f"Название: {apt.title}")
            print(f"Адрес: {apt.address}")
            print(f"Цена за день: {apt.price_per_day}")
            print(f"URL изображения: {apt.image_url}")
            print("-" * 50)

if __name__ == "__main__":
    check_apartments() 