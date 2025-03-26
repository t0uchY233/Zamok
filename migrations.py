from app import app, db
from flask_migrate import Migrate, upgrade

# Инициализация миграций
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        upgrade() 