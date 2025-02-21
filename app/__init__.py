from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Получаем абсолютный путь к директории проекта
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Инициализация Flask приложения
app = Flask(__name__,
    static_folder=os.path.join(basedir, 'frontend'),
    static_url_path='',
    template_folder=os.path.join(basedir, 'frontend')
)

# Конфигурация приложения
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///zamok.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)

# Импорт маршрутов
from app import routes, auth, booking

# Создание таблиц базы данных
with app.app_context():
    db.create_all() 