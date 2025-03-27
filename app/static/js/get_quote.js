document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quote-form');
    const calculateBtn = document.getElementById('calculate-btn');
    const bookingBtn = document.getElementById('booking-btn');
    const resultDiv = document.getElementById('quote-result');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Скрываем кнопку бронирования и результаты по умолчанию
    if (bookingBtn) bookingBtn.style.display = 'none';
    if (resultDiv) resultDiv.style.display = 'none';
    
    // Привязываем обработчик к кнопке расчета
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function(e) {
            e.preventDefault();
            calculatePrice();
        });
    }
    
    // Привязываем обработчик к кнопке бронирования
    if (bookingBtn) {
        bookingBtn.addEventListener('click', function(e) {
            e.preventDefault();
            submitBooking();
        });
    }
    
    // Функция для расчета стоимости
    function calculatePrice() {
        // Показываем индикатор загрузки
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        
        // Собираем данные из формы
        const apartmentId = document.getElementById('apartment-id').value;
        const checkInDate = document.getElementById('check-in-date').value;
        const checkOutDate = document.getElementById('check-out-date').value;
        
        // Проверяем, что все необходимые поля заполнены
        if (!apartmentId || !checkInDate || !checkOutDate) {
            showError('Пожалуйста, заполните все обязательные поля.');
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            return;
        }
        
        // Отправляем запрос на сервер
        fetch('/api/calculate-price', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                apartment_id: apartmentId,
                check_in_date: checkInDate,
                check_out_date: checkOutDate
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            // Скрываем индикатор загрузки
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            
            // Отображаем результаты
            showResult(data);
            
            // Показываем кнопку бронирования
            if (bookingBtn) bookingBtn.style.display = 'block';
        })
        .catch(error => {
            // Скрываем индикатор загрузки
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            
            // Отображаем ошибку
            showError(error.error || 'Произошла ошибка при расчете стоимости.');
        });
    }
    
    // Отправка данных на сервер при бронировании
    async function submitBooking() {
        // Собираем данные пользователя
        const name = document.getElementById('name').value;
        const phone = document.getElementById('phone').value;
        const email = document.getElementById('email').value;

        // Проверяем, что имя и телефон заполнены
        if (!name || !phone) {
            showMessage('Пожалуйста, заполните имя и телефон', 'error');
            return;
        }

        // Получаем общую стоимость
        const totalPrice = calculateTotalPrice();
        
        console.log('Отправка данных бронирования...');
        console.log('Выбранные апартаменты:', selectedApartment);
        console.log('Даты:', { check_in_date: checkInDate, check_out_date: checkOutDate });
        console.log('Информация о пользователе:', { name, phone, email });
        console.log('Общая стоимость:', totalPrice);

        try {
            // Отправляем данные на сервер
            const response = await fetch('/api/submit-quote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    apartment_id: selectedApartment.id,
                    dates: {
                        check_in_date: checkInDate,
                        check_out_date: checkOutDate
                    },
                    user_info: {
                        name: name,
                        phone: phone,
                        email: email
                    },
                    total_price: Number(totalPrice)
                })
            });

            const result = await response.json();

            if (response.ok) {
                // Успешное бронирование
                showMessage('Спасибо! Ваше бронирование успешно отправлено. Номер бронирования: ' + result.booking_id, 'success');
                
                // Скрываем форму бронирования и показываем форму расчета снова
                document.getElementById('booking-form').style.display = 'none';
                document.getElementById('calculation-form').style.display = 'block';
                
                // Очищаем поля формы
                document.getElementById('name').value = '';
                document.getElementById('phone').value = '';
                document.getElementById('email').value = '';
                
                // Сбрасываем выбранные даты и квартиру
                checkInDate = null;
                checkOutDate = null;
                selectedApartment = null;
                
                // Обновляем отображение
                updateDateDisplay();
                updateTotalPriceDisplay();
                
            } else {
                // Ошибка бронирования
                showMessage('Ошибка: ' + (result.error || 'Не удалось отправить бронирование'), 'error');
                console.error('Ошибка бронирования:', result);
            }
        } catch (error) {
            showMessage('Ошибка соединения. Пожалуйста, попробуйте позже.', 'error');
            console.error('Ошибка отправки данных:', error);
        }
    }
    
    // Функция для отображения результатов расчета
    function showResult(data) {
        if (!resultDiv) return;
        
        resultDiv.innerHTML = `
            <div class="alert alert-info">
                <h4>Стоимость бронирования:</h4>
                <p>Дата заезда: ${data.check_in_date}</p>
                <p>Дата выезда: ${data.check_out_date}</p>
                <p>Количество дней: ${data.num_days}</p>
                <p>Цена за сутки: ${data.price_per_day} руб.</p>
                <p>Итоговая стоимость: <strong id="total-price" data-value="${data.total_price}">${data.total_price} руб.</strong></p>
            </div>
        `;
        
        resultDiv.style.display = 'block';
        
        // Скроллим к результатам
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Функция для отображения ошибки
    function showError(message) {
        if (!resultDiv) return;
        
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <p><strong>Ошибка:</strong> ${message}</p>
            </div>
        `;
        
        resultDiv.style.display = 'block';
        
        // Скроллим к сообщению об ошибке
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Функция для отображения сообщения об успехе
    function showSuccess(message) {
        if (!resultDiv) return;
        
        resultDiv.innerHTML = `
            <div class="alert alert-success">
                <p><strong>Успех!</strong> ${message}</p>
            </div>
        `;
        
        resultDiv.style.display = 'block';
        
        // Скроллим к сообщению об успехе
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }
});

// Глобальные переменные для доступа из HTML
window.selectedApartmentId = null;
window.selectedPricePerDay = 0;
window.totalPrice = 0;

// Экспортируем функции в глобальную область видимости
window.selectApartment = selectApartment;
window.calculateTotal = calculateTotal;

// Функция для загрузки списка квартир
async function loadApartments() {
    console.log('Загрузка списка квартир...');
    try {
        const response = await fetch('/api/apartments');
        const data = await response.json();
        
        if (!Array.isArray(data)) {
            console.error('Неверный формат данных:', data);
            return;
        }
        
        console.log('Получены данные квартир:', data);
        
        const apartmentsContainer = document.getElementById('apartments-container');
        apartmentsContainer.innerHTML = data.map(apartment => `
            <div class="apartment-card">
                <img src="${apartment.image_url}" alt="${apartment.title}">
                <h3>${apartment.title}</h3>
                <p>${apartment.description}</p>
                <p>Цена: ${apartment.price_per_day} ₽/день</p>
                <button class="select-apartment-btn" data-id="${apartment.id}" data-price="${apartment.price_per_day}">Выбрать</button>
            </div>
        `).join('');
        
        // Добавляем обработчики для кнопок выбора
        document.querySelectorAll('.select-apartment-btn').forEach(button => {
            button.addEventListener('click', function() {
                const id = parseInt(this.getAttribute('data-id'));
                const price = parseInt(this.getAttribute('data-price'));
                selectApartment(id, price);
                console.log(`Выбрана квартира: ID=${id}, Цена=${price}`);
            });
        });
    } catch (error) {
        console.error('Ошибка при загрузке квартир:', error);
    }
}

// Функция выбора квартиры
function selectApartment(id, pricePerDay) {
    window.selectedApartmentId = id;
    window.selectedPricePerDay = pricePerDay;
    calculateTotal();
    
    // Визуально показываем, что квартира выбрана
    document.querySelectorAll('.apartment-card').forEach(card => {
        card.style.border = 'none';
    });
    
    const selectedButtons = document.querySelectorAll(`.select-apartment-btn[data-id="${id}"]`);
    if (selectedButtons.length > 0) {
        const card = selectedButtons[0].closest('.apartment-card');
        if (card) {
            card.style.border = '2px solid #28a745';
            card.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// Функция расчета стоимости
function calculateTotal() {
    const dates = document.getElementById('dates').value;
    console.log('Вызвана функция calculateTotal. Даты:', dates);
    
    if (!dates || !window.selectedApartmentId) {
        document.getElementById('total-price').textContent = '0 ₽';
        window.totalPrice = 0;
        return;
    }
    
    // Поддержка разных форматов разделителей для flatpickr
    let startStr, endStr;
    if (dates.includes(' to ')) {
        [startStr, endStr] = dates.split(' to ');
    } else if (dates.includes(' - ')) {
        [startStr, endStr] = dates.split(' - ');
    } else {
        // Если только одна дата, используем её как начало и конец
        startStr = endStr = dates;
    }
    
    if (!startStr || !endStr) {
        document.getElementById('total-price').textContent = '0 ₽';
        window.totalPrice = 0;
        return;
    }

    const start = new Date(startStr);
    const end = new Date(endStr);
    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    
    console.log('Расчет дней:', {
        startStr,
        endStr,
        start: start.toISOString(),
        end: end.toISOString(),
        days
    });
    
    if (days <= 0) {
        document.getElementById('total-price').textContent = '0 ₽';
        window.totalPrice = 0;
        return;
    }
    
    window.totalPrice = days * window.selectedPricePerDay;
    document.getElementById('total-price').textContent = `${window.totalPrice} ₽`;
    
    console.log('Расчет стоимости:', {
        startDate: startStr,
        endDate: endStr,
        days: days,
        pricePerDay: window.selectedPricePerDay,
        totalPrice: window.totalPrice
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Страница загружена, инициализация приложения...');
    
    loadApartments();
    
    // Инициализация выбора дат
    const fp = flatpickr("#dates", {
        mode: "range",
        dateFormat: "Y-m-d",
        minDate: "today",
        locale: {
            ...flatpickr.l10ns.ru,
            rangeSeparator: " - "
        },
        onChange: function(selectedDates, dateStr) {
            console.log('Выбраны даты:', dateStr);
            calculateTotal();
        },
        onReady: function() {
            console.log('Календарь инициализирован');
        }
    });
    
    console.log('Инициализация завершена, глобальное состояние:', {
        selectedApartmentId: window.selectedApartmentId,
        selectedPricePerDay: window.selectedPricePerDay,
        totalPrice: window.totalPrice
    });
}); 