from pyngrok import ngrok, conf
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def start_ngrok():
    """Запуск NGROK для проксирования Flask приложения"""
    # Получаем токен из переменных окружения или файла .env
    auth_token = os.getenv("NGROK_AUTHTOKEN")
    
    if auth_token:
        # Если токен существует, настраиваем ngrok
        conf.get_default().auth_token = auth_token
        
        # Запускаем туннель до Flask приложения (порт 5000)
        public_url = ngrok.connect(5000).public_url
        
        # Выводим информацию о туннеле
        print(f" * NGROK туннель запущен по адресу: {public_url}")
        
        return public_url
    else:
        # Если токен не существует, выводим предупреждение
        print(" * NGROK не запущен: не указан NGROK_AUTHTOKEN в .env файле")
        return None

if __name__ == "__main__":
    start_ngrok() 