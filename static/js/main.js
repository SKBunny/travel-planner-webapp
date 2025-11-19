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