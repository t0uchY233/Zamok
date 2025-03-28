# Папка для изображений квартир

В этой директории должны находиться изображения для квартир:

- apartment-1.jpg
- apartment-2.jpg
- apartment-3.jpg
- и другие

## Рекомендации

Для оптимальной работы с Next.js Image:

1. Рекомендуемый размер изображений: 1200x800 пикселей
2. Формат: WebP или JPEG
3. Размер файла: не более 200 КБ

## Скрипт для загрузки изображений

```bash
# Скрипт для загрузки заглушек изображений
mkdir -p public/images/apartments
curl -o public/images/apartments/apartment-1.jpg https://via.placeholder.com/1200x800.jpg?text=Apartment+1
curl -o public/images/apartments/apartment-2.jpg https://via.placeholder.com/1200x800.jpg?text=Apartment+2
curl -o public/images/apartments/apartment-3.jpg https://via.placeholder.com/1200x800.jpg?text=Apartment+3
```