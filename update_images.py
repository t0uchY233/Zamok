from app import app, db
from app.database import Apartment
from PIL import Image
import os

def optimize_image(input_path, output_path, max_size=(1600, 1000)):
    """Оптимизация изображения"""
    with Image.open(input_path) as img:
        # Сохраняем пропорции
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        # Сохраняем с оптимальным качеством
        img.save(output_path, 'JPEG', quality=85, optimize=True)

def update_image_urls():
    with app.app_context():
        # Путь к директории с изображениями
        images_dir = os.path.join('frontend', 'static', 'images', 'apartments')
        os.makedirs(images_dir, exist_ok=True)
        
        apartments = Apartment.query.all()
        for apt in apartments:
            # Формируем пути для изображений
            image_filename = f'apartment{apt.id}.jpg'
            image_path = os.path.join(images_dir, image_filename)
            
            # Если изображение существует, оптимизируем его
            if os.path.exists(image_path):
                temp_path = image_path + '.temp'
                optimize_image(image_path, temp_path)
                os.replace(temp_path, image_path)
            
            # Обновляем URL в базе данных
            apt.image_url = f'/static/images/apartments/{image_filename}'
        
        db.session.commit()
        print("URLs обновлены")
        print("\nИнструкция:")
        print(f"1. Поместите изображения квартир в директорию: {images_dir}")
        print("2. Названия файлов должны быть: apartment1.jpg, apartment2.jpg, apartment3.jpg")
        print("3. Рекомендуемое разрешение: 1600x1000px")
        print("4. После добавления изображений запустите скрипт повторно для оптимизации")

if __name__ == '__main__':
    update_image_urls() 