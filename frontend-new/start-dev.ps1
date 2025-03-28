# PowerShell скрипт для запуска frontend в режиме разработки на Windows

# Переход в директорию frontend-new
Set-Location -Path $PSScriptRoot

# Проверяем наличие директории для изображений
if (!(Test-Path -Path "./public/images/apartments")) {
    Write-Host "Создание директории для изображений квартир..." -ForegroundColor Green
    New-Item -ItemType Directory -Path "./public/images/apartments" -Force | Out-Null
}

# Создаем заглушки для изображений если их нет
$placeholders = @(
    "./public/images/apartments/apartment-1.jpg",
    "./public/images/apartments/apartment-2.jpg",
    "./public/images/apartments/apartment-3.jpg"
)

foreach ($placeholder in $placeholders) {
    if (!(Test-Path -Path $placeholder)) {
        Write-Host "Создание заглушки для $placeholder..." -ForegroundColor Yellow
        # Примечание: здесь должна быть команда для копирования или создания изображения-заглушки
        # Например: Copy-Item "./public/images/placeholder-apartment.jpg" -Destination $placeholder
        # В данном случае просто создаем пустой файл как временное решение
        New-Item -ItemType File -Path $placeholder -Force | Out-Null
    }
}

# Запуск Next.js сервера разработки
Write-Host "Запуск Next.js сервера разработки..." -ForegroundColor Cyan
npx next dev