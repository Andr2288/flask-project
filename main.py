from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from models import db, User, Post, Comment
from forms import LoginForm, RegistrationForm, PostForm, CommentForm, UserForm
from api import init_api


def create_app():
    """Фабрика додатків Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація розширень
    db.init_app(app)

    # Для навчального проекту можна відключити CSRF
    # csrf = CSRFProtect(app)

    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # Ініціалізація API
    api = init_api(app)

    return app, None, jwt, migrate, api


app, csrf, jwt, migrate, api = create_app()


# JWT обробники помилок
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Токен прострочений'}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Невідомий токен'}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Потрібна авторизація'}), 401


# Веб-маршрути з Flask-WTF
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Авторизація з Flask-WTF"""
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['current_user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
            flash(f'Ласкаво просимо, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Невірний email або пароль', 'error')

    return render_template('login_wtf.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Реєстрація з Flask-WTF"""
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        # Перший користувач стає адміном
        if User.query.count() == 0:
            user.is_admin = True

        db.session.add(user)
        db.session.commit()

        flash('Реєстрація успішна!', 'success')
        return redirect(url_for('login'))

    return render_template('register_wtf.html', form=form)


@app.route('/')
def index():
    """Головна сторінка"""
    if 'current_user' not in session:
        return redirect(url_for('login'))

    users = User.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('index.html', users=users, posts=posts)


@app.route('/posts/create', methods=['GET', 'POST'])
def create_post():
    """Створення поста з Flask-WTF"""
    if 'current_user' not in session:
        return redirect(url_for('login'))

    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=session['current_user']['id']
        )
        db.session.add(post)
        db.session.commit()

        flash('Пост створено!', 'success')
        return redirect(url_for('posts'))

    return render_template('create_post_wtf.html', form=form)


@app.route('/posts')
def posts():
    """Список постів"""
    if 'current_user' not in session:
        return redirect(url_for('login'))

    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def view_post(id):
    """Перегляд поста з коментарями"""
    if 'current_user' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.created_at.desc()).all()
    form = CommentForm()

    return render_template('view_post_wtf.html', post=post, comments=comments, form=form)


@app.route('/comments/create/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    """Створення коментаря з Flask-WTF"""
    if 'current_user' not in session:
        return redirect(url_for('login'))

    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post_id,
            user_id=session['current_user']['id']
        )
        db.session.add(comment)
        db.session.commit()
        flash('Коментар додано!', 'success')

    return redirect(url_for('view_post', id=post_id))


@app.route('/logout')
def logout():
    """Вихід з системи"""
    session.clear()
    flash('До побачення!', 'success')
    return redirect(url_for('login'))


@app.route('/api-docs')
def api_docs():
    """Документація API"""
    return """
    <h1>API Documentation</h1>
    <h2>Endpoints:</h2>
    <ul>
        <li><strong>POST /api/auth/login</strong> - Авторизація</li>
        <li><strong>GET /api/users</strong> - Список користувачів (адмін)</li>
        <li><strong>POST /api/users</strong> - Створити користувача (адмін)</li>
        <li><strong>GET /api/users/{id}</strong> - Інформація про користувача</li>
        <li><strong>PUT /api/users/{id}</strong> - Оновити користувача</li>
        <li><strong>DELETE /api/users/{id}</strong> - Видалити користувача (адмін)</li>
        <li><strong>GET /api/posts</strong> - Список постів</li>
        <li><strong>POST /api/posts</strong> - Створити пост</li>
        <li><strong>GET /api/posts/{id}</strong> - Пост з коментарями</li>
        <li><strong>PUT /api/posts/{id}</strong> - Оновити пост</li>
        <li><strong>DELETE /api/posts/{id}</strong> - Видалити пост</li>
    </ul>

    <h2>Aiohttp Server:</h2>
    <p>Запустіть окремо: python aiohttp_server.py</p>
    <ul>
        <li><strong>GET localhost:8080/api/async/posts</strong> - Асинхронні пости</li>
        <li><strong>GET localhost:8080/api/async/users</strong> - Асинхронні користувачі</li>
        <li><strong>GET localhost:8080/api/async/external/news</strong> - Зовнішній API</li>
    </ul>
    """


def start_aiohttp_server():
    """Запуск aiohttp сервера в окремому потоці"""
    print("💡 Для запуску aiohttp сервера виконайте:")
    print("   python aiohttp_server.py")
    print("   або")
    print("   python aiohttp_simple.py (без MySQL)")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    print("=" * 50)
    print("🚀 Flask додаток з усіма технологіями запущено!")
    print("=" * 50)
    print("✅ Реалізовано:")
    print("  - Python")
    print("  - Flask")
    print("  - MySQL")
    print("  - Flask-SQLAlchemy")
    print("  - Flask-WTF")
    print("  - Flask-JWT-Extended")
    print("  - Flask-RESTful")
    print("  - Flask-Migrate")
    print("  - jinja2")
    print("  - aiohttp (окремий сервер)")
    print("  - asyncio")
    print("=" * 50)
    print("📚 Корисні посилання:")
    print("  - Веб-інтерфейс: http://localhost:5000")
    print("  - API документація: http://localhost:5000/api-docs")
    print("  - Aiohttp сервер: python aiohttp_server.py (localhost:8080)")
    print("=" * 50)
    print("⚡ Міграції:")
    print("  flask db init")
    print("  flask db migrate -m 'Initial migration'")
    print("  flask db upgrade")
    print("=" * 50)

    # Можна запустити aiohttp в окремому потоці
    # threading.Thread(target=start_aiohttp_server, daemon=True).start()

    app.run(debug=True, host='0.0.0.0', port=5000)