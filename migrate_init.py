from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Ініціалізація для міграцій
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Імпорт моделей для міграцій
from models import User, Post, Comment

if __name__ == '__main__':
    # Команди для роботи з міграціями:

    # 1. Ініціалізація міграцій (один раз):
    # flask db init

    # 2. Створення нової міграції:
    # flask db migrate -m "Initial migration"

    # 3. Застосування міграції:
    # flask db upgrade

    # 4. Перегляд історії міграцій:
    # flask db history

    # 5. Повернення до попередньої міграції:
    # flask db downgrade

    print("Flask-Migrate налаштовано!")
    print("Використовуйте команди:")
    print("1. flask db init - ініціалізація")
    print("2. flask db migrate -m 'назва' - створити міграцію")
    print("3. flask db upgrade - застосувати міграцію")
    print("4. flask db downgrade - відкотити міграцію")

    app.run(debug=True)