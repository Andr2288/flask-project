from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Модель користувача"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Зв'язки
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Встановити пароль"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Перевірити пароль"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Конвертувати в словник для API"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    """Модель поста"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Зв'язки
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_comments=False):
        """Конвертувати в словник для API"""
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username,
            'comments_count': len(self.comments)
        }

        if include_comments:
            result['comments'] = [comment.to_dict() for comment in self.comments]

        return result

    def __repr__(self):
        return f'<Post {self.title}>'


class Comment(db.Model):
    """Модель коментаря"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        """Конвертувати в словник для API"""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username,
            'post_id': self.post_id
        }

    def __repr__(self):
        return f'<Comment {self.id}>'