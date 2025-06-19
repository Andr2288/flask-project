from main import app, db, User, Post, Comment
from datetime import datetime


def init_database():
    """Ініціалізує базу даних з тестовими даними включаючи авторизацію"""
    with app.app_context():
        # Створити таблиці
        db.create_all()

        # Перевірити чи є дані
        if User.query.count() > 0:
            print("База даних вже містить дані")
            return

        # Створити тестових користувачів з паролями
        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin_user.set_password('admin123')

        user1 = User(
            username='oleg_dev',
            email='oleg.developer@gmail.com',
            is_admin=False
        )
        user1.set_password('password123')

        user2 = User(
            username='marina_blog',
            email='marina.blogger@ukr.net',
            is_admin=False
        )
        user2.set_password('password123')

        user3 = User(
            username='alex_student',
            email='alex.student@edu.ua',
            is_admin=False
        )
        user3.set_password('password123')

        # Додаємо користувачів до бази
        db.session.add(admin_user)
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()

        # Створити тестові пости
        post1 = Post(
            title='Ласкаво просимо до нашого блогу!',
            content='Це перший пост у нашому блозі. Тут ми будемо ділитися цікавими думками, ідеями та досвідом. Сподіваємося, що вам сподобається наш контент і ви залишите свої коментарі. Будемо писати про технології, програмування, життя та багато іншого.',
            user_id=admin_user.id
        )

        post2 = Post(
            title='Основи Flask для початківців',
            content='Flask - це мікрофреймворк для Python, який дозволяє швидко створювати веб-додатки. Він простий у використанні та дуже гнучкий. У цьому пості розглянемо основні концепції: маршрутизація, шаблони, робота з базами даних. Flask ідеально підходить для навчання веб-розробки.',
            user_id=user2.id
        )

        post3 = Post(
            title='Секрети продуктивного програмування',
            content='Хочете стати більш продуктивним програмістом? Ось кілька корисних порад: використовуйте правильні інструменти, пишіть чистий код, вчіться нові технології, працюйте в команді, не бійтеся помилок. Головне - постійно розвиватися та практикуватися.',
            user_id=user1.id
        )

        post4 = Post(
            title='Важливість кібербезпеки в сучасному світі',
            content='Кібербезпека стає все більш важливою у нашому цифровому світі. Кожного дня хакери намагаються отримати доступ до персональних даних, фінансової інформації та корпоративних секретів. Тому важливо знати основи захисту себе в інтернеті.',
            user_id=user3.id
        )

        db.session.add(post1)
        db.session.add(post2)
        db.session.add(post3)
        db.session.add(post4)
        db.session.commit()

        # Створити тестові коментарі
        comment1 = Comment(
            content='Дуже цікавий пост! Дякую за корисну інформацію. Буду чекати на нові статті.',
            post_id=post1.id,
            user_id=user1.id
        )

        comment2 = Comment(
            content='Згоден з автором. Flask справді простий у вивченні. Сам почав з нього вивчати веб-розробку.',
            post_id=post2.id,
            user_id=admin_user.id
        )

        comment3 = Comment(
            content='Корисні поради! Особливо сподобався пункт про чистий код. Це дійсно важливо.',
            post_id=post3.id,
            user_id=user2.id
        )

        comment4 = Comment(
            content='Тема кібербезпеки дуже актуальна. Чи плануєте написати більше на цю тему?',
            post_id=post4.id,
            user_id=admin_user.id
        )

        comment5 = Comment(
            content='Супер! Саме те, що шукав для свого навчального проекту.',
            post_id=post2.id,
            user_id=user3.id
        )

        comment6 = Comment(
            content='Чудовий блог! Підписався на оновлення. Пишіть частіше!',
            post_id=post1.id,
            user_id=user2.id
        )

        db.session.add(comment1)
        db.session.add(comment2)
        db.session.add(comment3)
        db.session.add(comment4)
        db.session.add(comment5)
        db.session.add(comment6)
        db.session.commit()

        print("База даних успішно ініціалізована з тестовими даними та авторизацією!")
        print("\nТестові акаунти:")
        print("1. Адміністратор:")
        print("   Email: admin@example.com")
        print("   Пароль: admin123")
        print("\n2. Користувачі:")
        print("   Email: oleg.developer@gmail.com | Пароль: password123")
        print("   Email: marina.blogger@ukr.net | Пароль: password123")
        print("   Email: alex.student@edu.ua | Пароль: password123")


if __name__ == '__main__':
    init_database()