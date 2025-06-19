from main import app, db, User, Post, Comment
from datetime import datetime


def init_database():
    """Ініціалізує базу даних з тестовими даними"""
    with app.app_context():
        # Створити таблиці
        db.create_all()

        # Перевірити чи є дані
        if User.query.count() > 0:
            print("База даних вже містить дані")
            return

        # Створити тестових користувачів
        user1 = User(username='admin', email='admin@example.com')
        user2 = User(username='user1', email='user1@example.com')
        user3 = User(username='blogger', email='blogger@example.com')

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()

        # Створити тестові пости
        post1 = Post(
            title='Ласкаво просимо до нашого блогу!',
            content='Це перший пост у нашому блозі. Тут ми будемо ділитися цікавими думками та ідеями.',
            user_id=user1.id
        )

        post2 = Post(
            title='Про Flask та веб-розробку',
            content='Flask - це мікрофреймворк для Python, який дозволяє швидко створювати веб-додатки. Він простий у використанні та дуже гнучкий.',
            user_id=user3.id
        )

        post3 = Post(
            title='Майбутнє веб-технологій',
            content='Веб-технології розвиваються дуже швидко. Кожного дня з\'являються нові інструменти та підходи до розробки.',
            user_id=user2.id
        )

        db.session.add(post1)
        db.session.add(post2)
        db.session.add(post3)
        db.session.commit()

        # Створити тестові коментарі
        comment1 = Comment(
            content='Дуже цікавий пост! Дякую за інформацію.',
            post_id=post1.id,
            user_id=user2.id
        )

        comment2 = Comment(
            content='Згоден! Flask справді простий у використанні.',
            post_id=post2.id,
            user_id=user1.id
        )

        comment3 = Comment(
            content='Було б цікаво почитати більше про нові технології.',
            post_id=post3.id,
            user_id=user3.id
        )

        db.session.add(comment1)
        db.session.add(comment2)
        db.session.add(comment3)
        db.session.commit()

        print("База даних успішно ініціалізована з тестовими даними!")


if __name__ == '__main__':
    init_database()