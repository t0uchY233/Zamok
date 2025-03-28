# Zamok - Frontend Next.js

## Обзор

Фронтенд для проекта Zamok, построенный на Next.js и Shadcn/UI. Обеспечивает современный интерфейс для бронирования квартир.

## Исправленные проблемы

- ✅ Настроена работа с изображениями через Next.js Image component
- ✅ Временно отключены API запросы для разработки без бэкенда
- ✅ Добавлен скрипт для запуска в Windows PowerShell

## Запуск проекта

### Windows (PowerShell)

```powershell
# Перейти в директорию frontend-new
cd frontend-new

# Запустить скрипт для Windows
.\start-dev.ps1
```

### Linux/Mac

```bash
# Перейти в директорию frontend-new
cd frontend-new

# Создать директорию для изображений
mkdir -p public/images/apartments

# Скопировать заглушки изображений
cp public/images/placeholder-apartment.jpg public/images/apartments/apartment-1.jpg
cp public/images/placeholder-apartment.jpg public/images/apartments/apartment-2.jpg
cp public/images/placeholder-apartment.jpg public/images/apartments/apartment-3.jpg

# Запустить сервер разработки
npx next dev
```

## Известные проблемы

1. **Дублирование навигации**: Компонент "Замок" в хедере дублирует функцию "Главная".
2. **Дублирование панели**: При переходе на страницу "Квартиры" дублируется навигационная панель.
3. **Ошибки расчета стоимости**: При расчете стоимости бронирования могут возникать ошибки в консоли.

## Дальнейшие улучшения

- ⏳ Интеграция с бэкендом
- ⏳ Улучшение SEO с помощью _document.js
- ⏳ Оптимизация загрузки изображений
- ⏳ Добавление юнит-тестов