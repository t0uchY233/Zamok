from app import app
from ngrok_config import start_ngrok
import os
import sys

if __name__ == '__main__':
    # Если мы в режиме разработки, запускаем NGROK
    if os.getenv('FLASK_ENV') == 'development':
        try:
            public_url = start_ngrok()
            print(f" * Приложение доступно по адресу: {public_url}")
            # Здесь можно добавить логику для обновления webhook URL в Telegram Bot API
            
            # Обновляем базовый URL для API
            os.environ['API_BASE_URL'] = public_url
            
        except Exception as e:
            print(f" * Ошибка при запуске NGROK: {str(e)}", file=sys.stderr)
            print(" * Продолжаем без NGROK...", file=sys.stderr)
    
    # Запускаем Flask приложение
    app.run(host='0.0.0.0', port=5000) 