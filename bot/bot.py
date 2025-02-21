import os
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
env_path = Path(__file__).parent.parent / '.env'
logger.info(f"Путь к .env файлу: {env_path}")
logger.info(f"Файл существует: {env_path.exists()}")

# Читаем файл напрямую
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                logger.info(f"Загружена переменная {key}")

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

logger.info(f"Загруженный токен: {TELEGRAM_TOKEN}")
logger.info(f"API URL: {API_BASE_URL}")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        logger.info(f"Пользователь {update.effective_user.id} запустил бота")
        logger.info("Создаю клавиатуру...")
        
        # Проверяем доступность API
        try:
            response = requests.get(API_BASE_URL)
            logger.info(f"Статус API: {response.status_code}")
        except Exception as api_error:
            logger.error(f"Ошибка при проверке API: {str(api_error)}")
        
        keyboard = [
            [InlineKeyboardButton("�� Просмотр квартир", callback_data='view_apartments')],
            [InlineKeyboardButton("📝 Регистрация", callback_data='register')],
            [InlineKeyboardButton("📋 Мои бронирования", callback_data='my_bookings')]
        ]
        logger.info("Клавиатура создана успешно")
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.info("Отправляю приветственное сообщение...")
        
        await update.message.reply_text(
            "Добро пожаловать в Zamok! 🏠\n\n"
            "Здесь вы можете:\n"
            "• Просматривать доступные квартиры\n"
            "• Регистрироваться в системе\n"
            "• Управлять бронированиями\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
        logger.info("Сообщение отправлено успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике start: {str(e)}")
        logger.error(f"Тип ошибки: {type(e)}")
        logger.error(f"Детали ошибки:", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.\n"
            f"Детали ошибки: {str(e)}"
        )

async def view_apartments_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик просмотра квартир"""
    query = update.callback_query
    await query.answer()
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/apartments")
        if response.status_code == 200:
            apartments = response.json()
            message = "Доступные квартиры:\n\n"
            
            for apt in apartments:
                message += f"🏠 {apt.get('title', 'Без названия')}\n"
                message += f"📍 {apt.get('address', 'Адрес не указан')}\n"
                message += f"💰 {apt.get('price', 'Цена не указана')} руб/мес\n"
                message += f"📝 {apt.get('description', 'Описание отсутствует')}\n\n"
            
            await query.message.reply_text(message)
        else:
            await query.message.reply_text("Не удалось получить список квартир. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка при получении списка квартир: {str(e)}")
        await query.message.reply_text("Произошла ошибка при получении списка квартир.")

async def register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик процесса регистрации"""
    query = update.callback_query
    await query.answer()
    
    # Проверяем статус регистрации
    response = requests.get(f"{API_BASE_URL}/api/auth/status/{query.from_user.id}")
    if response.status_code == 200 and response.json()['is_verified']:
        await query.message.reply_text("Вы уже зарегистрированы и верифицированы в системе! ✅")
        return
    
    await query.message.reply_text(
        "Для регистрации необходимо загрузить фото паспорта или другого документа, "
        "удостоверяющего личность. 📄\n\n"
        "Пожалуйста, отправьте фото документа."
    )
    context.user_data['awaiting_document'] = True

async def handle_document_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загруженного фото документа"""
    if not context.user_data.get('awaiting_document'):
        return
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    # Загружаем фото
    photo_data = await file.download_as_bytearray()
    
    # Отправляем данные на сервер
    files = {'document_photo': ('document.jpg', photo_data, 'image/jpeg')}
    data = {
        'telegram_id': update.effective_user.id,
        'username': update.effective_user.username,
        'full_name': f"{update.effective_user.first_name} {update.effective_user.last_name or ''}"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/auth/register", files=files, data=data)
    
    if response.status_code == 200:
        await update.message.reply_text(
            "Документ успешно загружен! ✅\n"
            "Ваша заявка на регистрацию принята и будет рассмотрена администратором.\n"
            "Мы уведомим вас о результатах проверки."
        )
    else:
        await update.message.reply_text(
            "Произошла ошибка при загрузке документа. ❌\n"
            "Пожалуйста, попробуйте позже или обратитесь в поддержку."
        )
    
    context.user_data['awaiting_document'] = False

async def my_bookings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик просмотра бронирований"""
    query = update.callback_query
    await query.answer()
    
    # Проверяем статус регистрации
    response = requests.get(f"{API_BASE_URL}/api/auth/status/{query.from_user.id}")
    if response.status_code != 200 or not response.json()['is_verified']:
        await query.message.reply_text(
            "Для просмотра бронирований необходимо зарегистрироваться и пройти верификацию. ❌\n"
            "Используйте команду /start и выберите 'Регистрация'."
        )
        return
    
    # Здесь должен быть запрос к API для получения бронирований пользователя
    # Пока заглушка
    await query.message.reply_text(
        "Функция просмотра бронирований находится в разработке. 🔧\n"
        "Попробуйте позже!"
    )

def main():
    """Запуск бота"""
    try:
        logger.info("Запуск бота...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(view_apartments_handler, pattern="^view_apartments$"))
        application.add_handler(CallbackQueryHandler(register_handler, pattern="^register$"))
        application.add_handler(CallbackQueryHandler(my_bookings_handler, pattern="^my_bookings$"))
        application.add_handler(MessageHandler(filters.PHOTO, handle_document_photo))
        
        logger.info("Бот успешно настроен и запускается")
        # Запуск бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")

if __name__ == '__main__':
    main() 