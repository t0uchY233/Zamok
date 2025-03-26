from pyngrok import ngrok, conf
import os
from dotenv import load_dotenv

load_dotenv()

def start_ngrok():
    try:
        # Закрываем все существующие туннели
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            ngrok.disconnect(tunnel.public_url)
        
        # Запускаем NGROK на порту 5000 (порт Flask-приложения)
        tunnel = ngrok.connect(5000, bind_tls=True)
        public_url = tunnel.public_url
        print(f" * NGROK туннель запущен на {public_url}")
        return public_url
    except Exception as e:
        print(f" * Ошибка при запуске NGROK: {str(e)}")
        raise 