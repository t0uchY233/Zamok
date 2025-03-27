import threading
import time
import os
import subprocess
import signal
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Глобальные флаги для управления потоками
flask_running = True
bot_running = True

# Функция для запуска Flask-сервера
def run_flask():
    print("Запуск Flask-сервера...")
    flask_process = subprocess.Popen(["python", "run.py"])
    
    while flask_running:
        # Проверяем, что процесс все еще работает
        if flask_process.poll() is not None:
            print("Flask-сервер неожиданно остановился. Перезапуск...")
            flask_process = subprocess.Popen(["python", "run.py"])
        time.sleep(2)
    
    # Завершаем процесс при выходе
    if flask_process.poll() is None:
        print("Останавливаем Flask-сервер...")
        flask_process.terminate()
        flask_process.wait(10)
        if flask_process.poll() is None:
            flask_process.kill()

# Функция для запуска Telegram-бота
def run_bot():
    print("Запуск Telegram-бота...")
    bot_process = subprocess.Popen(["python", "bot/bot.py"])
    
    while bot_running:
        # Проверяем, что процесс все еще работает
        if bot_process.poll() is not None:
            print("Telegram-бот неожиданно остановился. Перезапуск...")
            bot_process = subprocess.Popen(["python", "bot/bot.py"])
        time.sleep(2)
    
    # Завершаем процесс при выходе
    if bot_process.poll() is None:
        print("Останавливаем Telegram-бота...")
        bot_process.terminate()
        bot_process.wait(10)
        if bot_process.poll() is None:
            bot_process.kill()

# Функция для запуска ngrok
def run_ngrok():
    print("Запуск ngrok...")
    ngrok_process = subprocess.Popen(["python", "ngrok_config.py"])
    
    while flask_running:
        # ngrok запускается один раз и не требует мониторинга
        time.sleep(5)
        break
    
    # Завершаем процесс при выходе
    if ngrok_process.poll() is None:
        print("Останавливаем ngrok...")
        ngrok_process.terminate()
        ngrok_process.wait(5)
        if ngrok_process.poll() is None:
            ngrok_process.kill()

# Обработчик сигналов для корректного завершения
def signal_handler(sig, frame):
    global flask_running, bot_running
    print("\nПолучен сигнал остановки. Завершаем работу всех компонентов...")
    flask_running = False
    bot_running = False
    time.sleep(3)  # Даем время на корректное завершение потоков
    sys.exit(0)

# Регистрируем обработчик для сигналов завершения
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Проверка наличия TELEGRAM_BOT_TOKEN
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("ОШИБКА: Не задан TELEGRAM_BOT_TOKEN в .env файле!")
        sys.exit(1)
    
    # Создаем и запускаем потоки
    flask_thread = threading.Thread(target=run_flask)
    bot_thread = threading.Thread(target=run_bot)
    ngrok_thread = threading.Thread(target=run_ngrok)
    
    flask_thread.daemon = True
    bot_thread.daemon = True
    ngrok_thread.daemon = True
    
    flask_thread.start()
    time.sleep(3)  # Даем время Flask-серверу запуститься
    ngrok_thread.start()
    time.sleep(3)  # Даем время ngrok установить туннель
    bot_thread.start()
    
    print("\n✅ Все компоненты запущены!")
    print("🌐 Flask-сервер работает на http://localhost:5000")
    print("🤖 Telegram-бот запущен")
    print("🔄 ngrok туннель настроен")
    print("ℹ️ Для завершения работы нажмите Ctrl+C\n")
    
    try:
        # Держим основной поток активным
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass  # Обработка Ctrl+C через signal_handler 