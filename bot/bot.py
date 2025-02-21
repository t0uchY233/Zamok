import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests
import json
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("🏠 Просмотр квартир", web_app=WebAppInfo(url=f"{API_BASE_URL}/apartments"))],
        [InlineKeyboardButton("📝 Регистрация", callback_data='register')],
        [InlineKeyboardButton("📋 Мои бронирования", callback_data='my_bookings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Добро пожаловать в Zamok! 🏠\n\n"
        "Здесь вы можете:\n"
        "• Просматривать доступные квартиры\n"
        "• Регистрироваться в системе\n"
        "• Управлять бронированиями\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

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
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(register_handler, pattern="^register$"))
    application.add_handler(CallbackQueryHandler(my_bookings_handler, pattern="^my_bookings$"))
    application.add_handler(MessageHandler(filters.PHOTO & filters.PHOTO, handle_document_photo))
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 