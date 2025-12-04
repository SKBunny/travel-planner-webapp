// Автоматичне закриття alert повідомлень через 5 секунд
setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        let bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Валідація дат у формі створення поїздки
document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    if (startDateInput && endDateInput) {
        // Встановлюємо мінімальну дату як сьогодні
        const today = new Date().toISOString().split('T')[0];
        startDateInput.setAttribute('min', today);

        // Коли змінюється дата початку
        startDateInput.addEventListener('change', function() {
            endDateInput.setAttribute('min', this.value);

            // Якщо дата закінчення менша за дату початку - очищаємо
            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = '';
            }
        });

        // Перевірка перед відправкою форми
        const form = startDateInput.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (endDateInput.value < startDateInput.value) {
                    e.preventDefault();
                    alert('Дата закінчення не може бути раніше дати початку!');
                }
            });
        }
    }
});

// ==================== FLASH MESSAGES ====================

// Автоматичне закриття alert повідомлень через 5 секунд
setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        let bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// ==================== DARK MODE ====================

// Перевірка збереженої теми при завантаженні
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeIcon();
    }
});

// Перемикач теми
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon();

    // Анімація перемикання
    const toggle = document.getElementById('themeToggle');
    toggle.style.transform = 'rotate(360deg)';
    setTimeout(() => {
        toggle.style.transform = 'rotate(0deg)';
    }, 300);
}

// Оновлення іконки теми
function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    if (document.body.classList.contains('dark-mode')) {
        icon.className = 'bi bi-sun-fill';
    } else {
        icon.className = 'bi bi-moon-stars';
    }
}

// ==================== DATE VALIDATION ====================

// Валідація дат у формах
document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    if (startDateInput && endDateInput) {
        const today = new Date().toISOString().split('T')[0];
        startDateInput.setAttribute('min', today);

        startDateInput.addEventListener('change', function() {
            endDateInput.setAttribute('min', this.value);

            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = '';
            }
        });

        const form = startDateInput.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (endDateInput.value < startDateInput.value) {
                    e.preventDefault();
                    alert('Дата закінчення не може бути раніше дати початку!');
                }
            });
        }
    }
});

// ==================== SMOOTH SCROLL ====================

// Плавна прокрутка для якорних посилань
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== TOOLTIPS ====================

// Ініціалізація Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});