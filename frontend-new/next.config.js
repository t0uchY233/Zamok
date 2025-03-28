/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  // Разрешаем импорты с расширениями .jsx
  pageExtensions: ['js', 'jsx'],
  // Конфигурация для изображений
  images: {
    domains: ['via.placeholder.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048]
  }
}

module.exports = nextConfig