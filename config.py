import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    # MySQL database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'admin'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '1234567890'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'flask_crud'

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False