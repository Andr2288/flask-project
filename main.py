from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:1234567890@localhost/flask_crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# JWT helper functions
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# Auth decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        if not token:
            flash('Для доступу потрібна авторизація', 'error')
            return redirect(url_for('login'))

        user_id = verify_token(token)
        if not user_id:
            flash('Невідомий токен. Увійдіть знову', 'error')
            return redirect(url_for('login'))

        current_user = User.query.get(user_id)
        if not current_user:
            flash('Користувача не знайдено', 'error')
            return redirect(url_for('login'))

        session['current_user'] = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin
        }
        return f(*args, **kwargs)

    return decorated_function


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Auth Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Валідація
        if not username or not email or not password:
            flash('Всі поля обов\'язкові', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Паролі не співпадають', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Пароль повинен містити мінімум 6 символів', 'error')
            return render_template('register.html')

        # Перевірка на існування користувача
        if User.query.filter_by(email=email).first():
            flash('Користувач з таким email вже існує', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Користувач з таким іменем вже існує', 'error')
            return render_template('register.html')

        # Створення користувача
        user = User(username=username, email=email)
        user.set_password(password)

        # Перший користувач стає адміном
        if User.query.count() == 0:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()

        flash('Реєстрація успішна! Тепер ви можете увійти', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Email та пароль обов\'язкові', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Генерація JWT токену
            token = generate_token(user.id)

            # Зберігання токену в cookie
            response = redirect(url_for('index'))
            response.set_cookie('jwt_token', token, httponly=True, max_age=7 * 24 * 60 * 60)  # 7 днів

            flash(f'Ласкаво просимо, {user.username}!', 'success')
            return response
        else:
            flash('Невірний email або пароль', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    response = redirect(url_for('login'))
    response.set_cookie('jwt_token', '', expires=0)
    session.clear()
    flash('Ви успішно вийшли з системи', 'success')
    return response


# Main Routes
@app.route('/')
@login_required
def index():
    users = User.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('index.html', users=users, posts=posts)


# User CRUD - тільки для адмінів
@app.route('/users')
@login_required
def users():
    if not session['current_user']['is_admin']:
        flash('Доступ заборонений. Потрібні права адміністратора', 'error')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not session['current_user']['is_admin']:
        flash('Доступ заборонений', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        # Перевірка на існування
        if User.query.filter_by(email=email).first():
            flash('Користувач з таким email вже існує', 'error')
            return render_template('create_user.html')

        if User.query.filter_by(username=username).first():
            flash('Користувач з таким іменем вже існує', 'error')
            return render_template('create_user.html')

        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Користувача створено!', 'success')
        return redirect(url_for('users'))

    return render_template('create_user.html')


@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not session['current_user']['is_admin'] and session['current_user']['id'] != id:
        flash('Доступ заборонений', 'error')
        return redirect(url_for('index'))

    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']

        # Тільки адмін може змінювати права адміністратора
        if session['current_user']['is_admin']:
            user.is_admin = 'is_admin' in request.form

        # Якщо введено новий пароль
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash('Користувача оновлено!', 'success')
        return redirect(url_for('users') if session['current_user']['is_admin'] else url_for('profile'))

    return render_template('edit_user.html', user=user)


@app.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not session['current_user']['is_admin']:
        flash('Доступ заборонений', 'error')
        return redirect(url_for('index'))

    user = User.query.get_or_404(id)

    # Не дозволяємо видаляти себе
    if user.id == session['current_user']['id']:
        flash('Ви не можете видалити себе', 'error')
        return redirect(url_for('users'))

    db.session.delete(user)
    db.session.commit()
    flash('Користувача видалено!', 'success')
    return redirect(url_for('users'))


# Post CRUD
@app.route('/posts')
@login_required
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=posts)


@app.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Автор поста - поточний користувач
        post = Post(title=title, content=content, user_id=session['current_user']['id'])
        db.session.add(post)
        db.session.commit()
        flash('Пост створено!', 'success')
        return redirect(url_for('posts'))

    return render_template('create_post.html')


@app.route('/posts/<int:id>')
@login_required
def view_post(id):
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.created_at.desc()).all()
    return render_template('view_post.html', post=post, comments=comments)


@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)

    # Перевірка прав доступу - автор або адмін
    if post.user_id != session['current_user']['id'] and not session['current_user']['is_admin']:
        flash('Ви можете редагувати тільки свої пости', 'error')
        return redirect(url_for('posts'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Пост оновлено!', 'success')
        return redirect(url_for('view_post', id=post.id))

    return render_template('edit_post.html', post=post)


@app.route('/posts/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)

    # Перевірка прав доступу - автор або адмін
    if post.user_id != session['current_user']['id'] and not session['current_user']['is_admin']:
        flash('Ви можете видаляти тільки свої пости', 'error')
        return redirect(url_for('posts'))

    db.session.delete(post)
    db.session.commit()
    flash('Пост видалено!', 'success')
    return redirect(url_for('posts'))


# Comment CRUD
@app.route('/comments/create/<int:post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    content = request.form['content']

    if not content.strip():
        flash('Коментар не може бути порожнім', 'error')
        return redirect(url_for('view_post', id=post_id))

    # Автор коментаря - поточний користувач
    comment = Comment(content=content, post_id=post_id, user_id=session['current_user']['id'])
    db.session.add(comment)
    db.session.commit()
    flash('Коментар додано!', 'success')
    return redirect(url_for('view_post', id=post_id))


@app.route('/comments/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)

    # Перевірка прав доступу - автор коментаря або адмін
    if comment.user_id != session['current_user']['id'] and not session['current_user']['is_admin']:
        flash('Ви можете видаляти тільки свої коментарі', 'error')
        return redirect(url_for('view_post', id=comment.post_id))

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Коментар видалено!', 'success')
    return redirect(url_for('view_post', id=post_id))


# Profile route
@app.route('/profile')
@login_required
def profile():
    current_user = User.query.get(session['current_user']['id'])
    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    user_comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).limit(10).all()

    stats = {
        'posts_count': len(user_posts),
        'comments_count': Comment.query.filter_by(user_id=current_user.id).count(),
        'join_date': current_user.created_at.strftime('%d.%m.%Y')
    }

    return render_template('profile.html', user=current_user, posts=user_posts, comments=user_comments, stats=stats)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)