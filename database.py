import aiosqlite
import os

DB_PATH = 'database/users.db'

async def init_db():
    os.makedirs('database', exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'ru',
                is_subscribed INTEGER DEFAULT 0,
                got_algorithm INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def add_user(user_id: int, username: str, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username, language) VALUES (?, ?, ?)',
            (user_id, username, language)
        )
        await db.commit()

async def update_subscription(user_id: int, status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET is_subscribed = ? WHERE user_id = ?',
            (1 if status else 0, user_id)
        )
        await db.commit()

async def update_algorithm_status(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET got_algorithm = 1 WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()

async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT language FROM users WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 'ru'

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            total_users = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT COUNT(*) FROM users WHERE got_algorithm = 1') as cursor:
            got_algorithm = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT language, COUNT(*) FROM users GROUP BY language') as cursor:
            lang_stats = await cursor.fetchall()
        
        return {
            'total_users': total_users,
            'got_algorithm': got_algorithm,
            'lang_stats': lang_stats
        }