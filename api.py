from flask import request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import User, Post, Comment, db
from datetime import timedelta


class AuthAPI(Resource):
    def post(self):
        """Авторизація через API"""
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Email та пароль обов\'язкові'}, 400

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(days=7)
            )
            return {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            }, 200

        return {'message': 'Невірний email або пароль'}, 401


class UserListAPI(Resource):
    @jwt_required()
    def get(self):
        """Отримати список користувачів"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user.is_admin:
            return {'message': 'Доступ заборонений'}, 403

        users = User.query.all()
        return {
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat()
            } for user in users]
        }, 200

    @jwt_required()
    def post(self):
        """Створити нового користувача"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user.is_admin:
            return {'message': 'Доступ заборонений'}, 403

        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('is_admin', False)

        if not username or not email or not password:
            return {'message': 'Всі поля обов\'язкові'}, 400

        if User.query.filter_by(email=email).first():
            return {'message': 'Email вже використовується'}, 400

        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return {'message': 'Користувача створено', 'user_id': user.id}, 201


class UserAPI(Resource):
    @jwt_required()
    def get(self, user_id):
        """Отримати інформацію про користувача"""
        user = User.query.get_or_404(user_id)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat()
        }, 200

    @jwt_required()
    def put(self, user_id):
        """Оновити користувача"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if user_id != current_user_id and not current_user.is_admin:
            return {'message': 'Доступ заборонений'}, 403

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)

        if current_user.is_admin:
            user.is_admin = data.get('is_admin', user.is_admin)

        if data.get('password'):
            user.set_password(data['password'])

        db.session.commit()
        return {'message': 'Користувача оновлено'}, 200

    @jwt_required()
    def delete(self, user_id):
        """Видалити користувача"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user.is_admin:
            return {'message': 'Доступ заборонений'}, 403

        if user_id == current_user_id:
            return {'message': 'Не можна видалити себе'}, 400

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'Користувача видалено'}, 200


class PostListAPI(Resource):
    def get(self):
        """Отримати список постів"""
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return {
            'posts': [{
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'created_at': post.created_at.isoformat(),
                'comments_count': len(post.comments)
            } for post in posts]
        }, 200

    @jwt_required()
    def post(self):
        """Створити новий пост"""
        current_user_id = get_jwt_identity()
        data = request.get_json()

        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return {'message': 'Заголовок та зміст обов\'язкові'}, 400

        post = Post(title=title, content=content, user_id=current_user_id)
        db.session.add(post)
        db.session.commit()

        return {'message': 'Пост створено', 'post_id': post.id}, 201


class PostAPI(Resource):
    def get(self, post_id):
        """Отримати пост з коментарями"""
        post = Post.query.get_or_404(post_id)
        return {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'created_at': post.created_at.isoformat(),
            'comments': [{
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'created_at': comment.created_at.isoformat()
            } for comment in post.comments]
        }, 200

    @jwt_required()
    def put(self, post_id):
        """Оновити пост"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        post = Post.query.get_or_404(post_id)

        if post.user_id != current_user_id and not current_user.is_admin:
            return {'message': 'Доступ заборонений'}, 403

        data = request.get_json()
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)

        db.session.commit()
        return {'message': 'Пост оновлено'}, 200

    @jwt_required()
    def delete(self, post_id):
        """Видалити пост"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        post = Post.query.get_or_404(post_id)

        if post.user_id != current_user_id and not current_user.is_admin:
            return {'message': 'Доступ заборонений'}, 403

        db.session.delete(post)
        db.session.commit()
        return {'message': 'Пост видалено'}, 200


def init_api(app):
    """Ініціалізація API"""
    api = Api(app)

    # Auth endpoints
    api.add_resource(AuthAPI, '/api/auth/login')

    # User endpoints
    api.add_resource(UserListAPI, '/api/users')
    api.add_resource(UserAPI, '/api/users/<int:user_id>')

    # Post endpoints
    api.add_resource(PostListAPI, '/api/posts')
    api.add_resource(PostAPI, '/api/posts/<int:post_id>')

    return api