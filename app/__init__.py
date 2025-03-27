from flask import Flask, send_from_directory
import sqlite3
import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from flask_cors import CORS

# Загрузка переменных окружения
from dotenv import load_dotenv
load_dotenv()

# Получаем абсолютный путь к директории проекта
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Путь к БД SQLite
db_path = os.path.join(basedir, 'instance', 'zamok.db')

# Функция для подключения к БД
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Функция для инициализации БД (создание таблиц если не существуют)
def init_db():
    # Проверяем, существует ли директория для БД
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создаем необходимые таблицы, если они не существуют
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            telegram_id INTEGER UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            email TEXT,
            is_verified BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            address TEXT NOT NULL,
            description TEXT,
            price_per_day INTEGER NOT NULL,
            image_url TEXT,
            is_available BOOLEAN DEFAULT 1,
            owner_id INTEGER,
            smart_lock_id TEXT,
            FOREIGN KEY (owner_id) REFERENCES owners (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            apartment_id INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            total_price INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (apartment_id) REFERENCES apartments (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            payment_method TEXT,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Инициализация Flask приложения
app = Flask(__name__,
    static_folder='static',  # явно указываем папку для статических файлов
    static_url_path='/static',  # и URL-префикс для них
    template_folder=os.path.join(basedir, 'frontend')
)

# Включаем CORS
CORS(app)

# Настройка приложения
app.config['DEBUG'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # отключаем кэширование статики

# Добавляем дополнительную папку для статических файлов
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(basedir, 'frontend', 'static'), filename)

# Конфигурация приложения
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Настройка логирования
def setup_logging():
    # Создаем папку для логов, если её нет
    logs_dir = os.path.join(basedir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Настраиваем форматтер логов
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [в %(filename)s:%(lineno)d]'
    )
    
    # Настраиваем обработчик файловых логов
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'zamok.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Настраиваем обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Настраиваем логгер Flask
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Логируем запуск приложения
    app.logger.info('Zamok started')
    app.logger.info(f'Environment: {os.getenv("FLASK_ENV", "production")}')

# Вызываем настройку логирования
setup_logging()

# Инициализируем БД
init_db()

# Импорт маршрутов
from app import routes 