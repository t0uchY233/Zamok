/**
 * Zamok - Общие JavaScript утилиты для приложения
 */

// Инициализация Telegram Mini App
const ZamokApp = {
    // Инициализация
    init() {
        this.webapp = window.Telegram.WebApp;
        this.webapp.ready();
        this.user = this.webapp.initDataUnsafe.user;
        
        // Настраиваем тему Telegram
        this.webapp.setHeaderColor('secondary_bg_color');
        this.webapp.expand();
        
        return this;
    },
    
    // Показать всплывающее сообщение об успехе
    showSuccess(message, duration = 3000) {
        const element = document.getElementById('success-message');
        if (!element) {
            console.warn('Элемент success-message не найден на странице');
            return;
        }
        
        element.textContent = message;
        element.style.display = 'block';
        
        setTimeout(() => {
            element.style.display = 'none';
        }, duration);
    },
    
    // Показать всплывающее сообщение об ошибке
    showError(message, duration = 3000) {
        const element = document.getElementById('error-message');
        if (!element) {
            console.warn('Элемент error-message не найден на странице');
            return;
        }
        
        element.textContent = message;
        element.style.display = 'block';
        
        setTimeout(() => {
            element.style.display = 'none';
        }, duration);
    },
    
    // Анимация появления элементов
    animateElements(selector = '.card, .button, .form-group', delay = 50) {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, delay * index);
        });
    },
    
    // API запросы
    api: {
        // Обертка для fetch с обработкой ошибок
        async fetch(url, options = {}) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `HTTP ошибка ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error(`API ошибка (${url}):`, error);
                throw error;
            }
        },
        
        // GET запрос
        get(url) {
            return this.fetch(url);
        },
        
        // POST запрос
        post(url, data) {
            return this.fetch(url, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        // PUT запрос
        put(url, data) {
            return this.fetch(url, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        // DELETE запрос
        delete(url) {
            return this.fetch(url, {
                method: 'DELETE'
            });
        }
    },
    
    // Форматирование
    format: {
        // Форматирование даты
        date(dateString) {
            if (!dateString) return '';
            return new Date(dateString).toLocaleDateString();
        },
        
        // Форматирование валюты
        currency(value) {
            if (value === null || value === undefined) return '';
            return `${value} ₽`;
        },
        
        // Сокращение текста
        truncate(text, maxLength = 100) {
            if (!text || text.length <= maxLength) return text;
            return text.slice(0, maxLength) + '...';
        }
    },
    
    // Управление состоянием
    storage: {
        // Сохранение в localStorage
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Ошибка сохранения в localStorage:', error);
                return false;
            }
        },
        
        // Получение из localStorage
        get(key, defaultValue = null) {
            try {
                const value = localStorage.getItem(key);
                return value ? JSON.parse(value) : defaultValue;
            } catch (error) {
                console.error('Ошибка получения из localStorage:', error);
                return defaultValue;
            }
        },
        
        // Удаление из localStorage
        remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Ошибка удаления из localStorage:', error);
                return false;
            }
        },
        
        // Очистка всего localStorage
        clear() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                console.error('Ошибка очистки localStorage:', error);
                return false;
            }
        }
    },
    
    // Вспомогательные функции
    utils: {
        // Задержка выполнения (промис)
        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },
        
        // Создание уникального ID
        generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        },
        
        // Ленивая загрузка изображений
        setupLazyLoading() {
            const images = document.querySelectorAll('[data-src]');
            
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            img.src = img.dataset.src;
                            observer.unobserve(img);
                        }
                    });
                });
                
                images.forEach(img => observer.observe(img));
            } else {
                // Запасной вариант для старых браузеров
                images.forEach(img => {
                    img.src = img.dataset.src;
                });
            }
        },
        
        // Перехват отправки формы
        handleFormSubmit(formId, callback) {
            const form = document.getElementById(formId);
            if (!form) return;
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const data = {};
                
                for (const [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                await callback(data, form);
            });
        }
    }
};

// Экспорт для использования в других скриптах
window.ZamokApp = ZamokApp; 