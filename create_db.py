from app import app, db
from app.database import User, Apartment, Booking, Payment, Owner

def create_database():
    with app.app_context():
        db.create_all()
        print("База данных создана успешно")

if __name__ == "__main__":
    create_database() 