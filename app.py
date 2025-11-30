from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Ініціалізація Flask додатку
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ініціалізація розширень
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ============= МОДЕЛІ БАЗИ ДАНИХ =============

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Зв'язок з поїздками
    trips = db.relationship('Trip', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Зв'язок з користувачем
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    activities = db.relationship('Activity', backref='trip', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Trip {self.title}>'


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(10))  # Наприклад: "09:00"
    location = db.Column(db.String(200))
    cost = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), default='general')  # transport, food, activity, accommodation
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Зв'язок з поїздкою
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)

    def __repr__(self):
        return f'<Activity {self.title}>'
# ============= LOGIN MANAGER =============

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============= МАРШРУТИ (ROUTES) =============

# Головна сторінка
@app.route('/')
def index():
    return render_template('index.html')


# Реєстрація
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Перевірка чи існує користувач
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email вже зареєстрований', 'danger')
            return redirect(url_for('register'))

        # Створення нового користувача
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Вхід
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Успішний вхід!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Невірний email або пароль', 'danger')

    return render_template('login.html')


# Вихід
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи', 'info')
    return redirect(url_for('index'))


# Особистий кабінет
@app.route('/dashboard')
@login_required
def dashboard():
    trips = Trip.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', trips=trips)


# Створення поїздки
@app.route('/trip/new', methods=['GET', 'POST'])
@login_required
def new_trip():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        destination = request.form.get('destination', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        budget_str = request.form.get('budget', '0')

        # Серверна валідація
        if not title or not destination:
            flash('Назва та напрямок є обов\'язковими полями', 'danger')
            return render_template('trip.html')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Перевірка логічності дат
            if end_date < start_date:
                flash('Дата закінчення не може бути раніше дати початку', 'danger')
                return render_template('trip.html')

            budget = float(budget_str)
            if budget < 0:
                flash('Бюджет не може бути від\'ємним', 'danger')
                return render_template('trip.html')

        except ValueError:
            flash('Невірний формат дати або бюджету', 'danger')
            return render_template('trip.html')

        new_trip = Trip(
            title=title,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            user_id=current_user.id
        )

        db.session.add(new_trip)
        db.session.commit()

        flash('Поїздку створено!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('trip.html')


# Перегляд поїздки
@app.route('/trip/<int:trip_id>')
@login_required
def view_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('У вас немає доступу до цієї поїздки', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('trip_view.html', trip=trip)


# Редагування поїздки
@app.route('/trip/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    # Перевірка доступу
    if trip.user_id != current_user.id:
        flash('У вас немає доступу до цієї поїздки', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        destination = request.form.get('destination', '').strip()
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        budget_str = request.form.get('budget', '0')

        # Валідація
        if not title or not destination:
            flash('Назва та напрямок є обов\'язковими', 'danger')
            return render_template('trip_edit.html', trip=trip)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            if end_date < start_date:
                flash('Дата закінчення не може бути раніше дати початку', 'danger')
                return render_template('trip_edit.html', trip=trip)

            budget = float(budget_str)
            if budget < 0:
                flash('Бюджет не може бути від\'ємним', 'danger')
                return render_template('trip_edit.html', trip=trip)

            # Оновлення даних
            trip.title = title
            trip.destination = destination
            trip.start_date = start_date
            trip.end_date = end_date
            trip.budget = budget

            db.session.commit()
            flash('Поїздку оновлено!', 'success')
            return redirect(url_for('view_trip', trip_id=trip.id))

        except ValueError:
            flash('Невірний формат дати або бюджету', 'danger')
            return render_template('trip_edit.html', trip=trip)

    return render_template('trip_edit.html', trip=trip)


# Видалення поїздки
@app.route('/trip/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    # Перевірка доступу
    if trip.user_id != current_user.id:
        flash('У вас немає доступу до цієї поїздки', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(trip)
    db.session.commit()

    flash('Поїздку видалено', 'info')
    return redirect(url_for('dashboard'))


# Додавання активності
@app.route('/trip/<int:trip_id>/activity/new', methods=['GET', 'POST'])
@login_required
def new_activity(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    if trip.user_id != current_user.id:
        flash('У вас немає доступу до цієї поїздки', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date')
        time = request.form.get('time', '').strip()
        location = request.form.get('location', '').strip()
        cost_str = request.form.get('cost', '0')
        category = request.form.get('category', 'general')

        if not title or not date_str:
            flash('Назва та дата є обов\'язковими', 'danger')
            return render_template('activity_form.html', trip=trip)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')

            # Перевірка, чи дата в межах поїздки
            if date.date() < trip.start_date.date() or date.date() > trip.end_date.date():
                flash('Дата активності повинна бути в межах дат поїздки', 'danger')
                return render_template('activity_form.html', trip=trip)

            cost = float(cost_str)

            new_activity = Activity(
                title=title,
                description=description,
                date=date,
                time=time,
                location=location,
                cost=cost,
                category=category,
                trip_id=trip.id
            )

            db.session.add(new_activity)
            db.session.commit()

            flash('Активність додано!', 'success')
            return redirect(url_for('view_trip', trip_id=trip.id))

        except ValueError:
            flash('Невірний формат даних', 'danger')
            return render_template('activity_form.html', trip=trip)

    return render_template('activity_form.html', trip=trip)


# Редагування активності
@app.route('/trip/<int:trip_id>/activity/<int:activity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_activity(trip_id, activity_id):
    trip = Trip.query.get_or_404(trip_id)
    activity = Activity.query.get_or_404(activity_id)

    if trip.user_id != current_user.id or activity.trip_id != trip.id:
        flash('У вас немає доступу', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date')
        time = request.form.get('time', '').strip()
        location = request.form.get('location', '').strip()
        cost_str = request.form.get('cost', '0')
        category = request.form.get('category', 'general')

        if not title or not date_str:
            flash('Назва та дата є обов\'язковими', 'danger')
            return render_template('activity_form.html', trip=trip, activity=activity)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')

            if date.date() < trip.start_date.date() or date.date() > trip.end_date.date():
                flash('Дата активності повинна бути в межах дат поїздки', 'danger')
                return render_template('activity_form.html', trip=trip, activity=activity)

            cost = float(cost_str)

            activity.title = title
            activity.description = description
            activity.date = date
            activity.time = time
            activity.location = location
            activity.cost = cost
            activity.category = category

            db.session.commit()

            flash('Активність оновлено!', 'success')
            return redirect(url_for('view_trip', trip_id=trip.id))

        except ValueError:
            flash('Невірний формат даних', 'danger')
            return render_template('activity_form.html', trip=trip, activity=activity)

    return render_template('activity_form.html', trip=trip, activity=activity)


# Видалення активності
@app.route('/trip/<int:trip_id>/activity/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(trip_id, activity_id):
    trip = Trip.query.get_or_404(trip_id)
    activity = Activity.query.get_or_404(activity_id)

    if trip.user_id != current_user.id or activity.trip_id != trip.id:
        flash('У вас немає доступу', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(activity)
    db.session.commit()

    flash('Активність видалено', 'info')
    return redirect(url_for('view_trip', trip_id=trip.id))


# Позначити активність як виконану
@app.route('/trip/<int:trip_id>/activity/<int:activity_id>/toggle', methods=['POST'])
@login_required
def toggle_activity(trip_id, activity_id):
    trip = Trip.query.get_or_404(trip_id)
    activity = Activity.query.get_or_404(activity_id)

    if trip.user_id != current_user.id or activity.trip_id != trip.id:
        flash('У вас немає доступу', 'danger')
        return redirect(url_for('dashboard'))

    activity.completed = not activity.completed
    db.session.commit()

    return redirect(url_for('view_trip', trip_id=trip.id))


# Статистика поїздки
@app.route('/trip/<int:trip_id>/statistics')
@login_required
def trip_statistics(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    if trip.user_id != current_user.id:
        flash('У вас немає доступу до цієї поїздки', 'danger')
        return redirect(url_for('dashboard'))

    # Статистика по категоріях
    stats = {
        'transport': 0,
        'food': 0,
        'activity': 0,
        'accommodation': 0,
        'shopping': 0,
        'general': 0
    }

    for activity in trip.activities:
        if activity.category in stats:
            stats[activity.category] += activity.cost

    total_spent = sum(stats.values())
    remaining = trip.budget - total_spent

    # Відсоток виконаних активностей
    total_activities = len(trip.activities)
    completed_activities = len([a for a in trip.activities if a.completed])
    completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0

    return render_template('trip_statistics.html',
                           trip=trip,
                           stats=stats,
                           total_spent=total_spent,
                           remaining=remaining,
                           completion_rate=completion_rate,
                           total_activities=total_activities,
                           completed_activities=completed_activities)

# ============= ЗАПУСК ДОДАТКУ =============

if __name__ == '__main__':
    # Створення всіх таблиць в базі даних
    with app.app_context():
        db.create_all()
        print("База даних створена успішно!")

    # Запуск сервера
    app.run(debug=True, host='0.0.0.0', port=5001)