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

    def __repr__(self):
        return f'<Trip {self.title}>'


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
        title = request.form.get('title')
        destination = request.form.get('destination')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        budget = float(request.form.get('budget', 0))

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


# ============= ЗАПУСК ДОДАТКУ =============

if __name__ == '__main__':
    # Створення всіх таблиць в базі даних
    with app.app_context():
        db.create_all()
        print("База даних створена успішно!")

    # Запуск сервера
    app.run(debug=True, host='0.0.0.0', port=5001)