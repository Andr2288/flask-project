import asyncio
import aiohttp
from aiohttp import web, ClientSession
import aiohttp_cors
import json
import aiomysql
from datetime import datetime


class AsyncBlogAPI:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        self.db_config = {
            'host': 'localhost',
            'user': 'admin',
            'password': '1234567890',
            'database': 'flask_crud'
        }

    def setup_routes(self):
        """Налаштування маршрутів"""
        self.app.router.add_get('/api/async/posts', self.get_posts)
        self.app.router.add_get('/api/async/posts/{post_id}', self.get_post)
        self.app.router.add_get('/api/async/users', self.get_users)
        self.app.router.add_get('/api/async/external/news', self.get_external_news)

    def setup_cors(self):
        """Налаштування CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        for route in list(self.app.router.routes()):
            cors.add(route)

    async def get_db_connection(self):
        """Отримати з'єднання з БД"""
        return await aiomysql.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            db=self.db_config['database'],
            autocommit=True
        )

    async def get_posts(self, request):
        """Отримати всі пости асинхронно"""
        try:
            conn = await self.get_db_connection()
            cursor = await conn.cursor(dictionary=True)

            query = """
                SELECT p.id, p.title, p.content, p.created_at, 
                       u.username as author_name,
                       COUNT(c.id) as comments_count
                FROM post p
                LEFT JOIN user u ON p.user_id = u.id
                LEFT JOIN comment c ON p.id = c.post_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
            """

            await cursor.execute(query)
            posts = await cursor.fetchall()

            # Конвертація datetime в string
            for post in posts:
                if post['created_at']:
                    post['created_at'] = post['created_at'].isoformat()

            await cursor.close()
            await conn.close()

            return web.json_response({
                'success': True,
                'posts': posts,
                'count': len(posts)
            })

        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def get_post(self, request):
        """Отримати конкретний пост з коментарями"""
        post_id = request.match_info['post_id']

        try:
            conn = await self.get_db_connection()
            cursor = await conn.cursor(dictionary=True)

            # Отримуємо пост
            post_query = """
                SELECT p.id, p.title, p.content, p.created_at, 
                       u.username as author_name
                FROM post p
                LEFT JOIN user u ON p.user_id = u.id
                WHERE p.id = %s
            """

            await cursor.execute(post_query, (post_id,))
            post = await cursor.fetchone()

            if not post:
                return web.json_response({
                    'success': False,
                    'error': 'Пост не знайдено'
                }, status=404)

            # Отримуємо коментарі
            comments_query = """
                SELECT c.id, c.content, c.created_at,
                       u.username as author_name
                FROM comment c
                LEFT JOIN user u ON c.user_id = u.id
                WHERE c.post_id = %s
                ORDER BY c.created_at DESC
            """

            await cursor.execute(comments_query, (post_id,))
            comments = await cursor.fetchall()

            # Конвертація datetime
            post['created_at'] = post['created_at'].isoformat()
            for comment in comments:
                comment['created_at'] = comment['created_at'].isoformat()

            post['comments'] = comments

            await cursor.close()
            await conn.close()

            return web.json_response({
                'success': True,
                'post': post
            })

        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def get_users(self, request):
        """Отримати список користувачів"""
        try:
            conn = await self.get_db_connection()
            cursor = await conn.cursor(dictionary=True)

            query = """
                SELECT u.id, u.username, u.email, u.is_admin, u.created_at,
                       COUNT(p.id) as posts_count
                FROM user u
                LEFT JOIN post p ON u.id = p.user_id
                GROUP BY u.id
                ORDER BY u.created_at DESC
            """

            await cursor.execute(query)
            users = await cursor.fetchall()

            # Конвертація datetime та bool
            for user in users:
                user['created_at'] = user['created_at'].isoformat()
                user['is_admin'] = bool(user['is_admin'])

            await cursor.close()
            await conn.close()

            return web.json_response({
                'success': True,
                'users': users,
                'count': len(users)
            })

        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    async def get_external_news(self, request):
        """Приклад роботи з зовнішнім API"""
        try:
            async with ClientSession() as session:
                # Приклад запиту до зовнішнього API
                url = 'https://jsonplaceholder.typicode.com/posts'

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Беремо тільки перші 5 постів
                        limited_data = data[:5]

                        return web.json_response({
                            'success': True,
                            'external_posts': limited_data,
                            'source': 'JSONPlaceholder API'
                        })
                    else:
                        return web.json_response({
                            'success': False,
                            'error': 'Помилка при отриманні даних'
                        }, status=500)

        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)


async def init_app():
    """Ініціалізація додатку"""
    blog_api = AsyncBlogAPI()
    return blog_api.app


async def main():
    """Запуск сервера"""
    app = await init_app()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    print("Aiohttp сервер запущено на http://localhost:8080")
    print("Доступні endpoints:")
    print("- GET /api/async/posts - всі пости")
    print("- GET /api/async/posts/{id} - конкретний пост")
    print("- GET /api/async/users - всі користувачі")
    print("- GET /api/async/external/news - зовнішній API")

    # Тримаємо сервер запущеним
    try:
        await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()


if __name__ == '__main__':
    # Встановіть необхідні пакети:
    # pip install aiohttp aiohttp-cors aiomysql
    asyncio.run(main())