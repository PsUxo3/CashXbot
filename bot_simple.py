import asyncio
import logging
import aiosqlite
import os
import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID_RU = int(os.getenv('CHANNEL_ID_RU', '-1001234567890'))  # Канал для русских
CHANNEL_ID_EN = int(os.getenv('CHANNEL_ID_EN', '-1000987654321'))  # Канал для англичан
CHANNEL_USERNAME_RU = os.getenv('CHANNEL_USERNAME_RU', '@russian_channel')
CHANNEL_USERNAME_EN = os.getenv('CHANNEL_USERNAME_EN', '@english_channel')
REF_LINK = os.getenv('REF_LINK')
MAIN_PROMO = os.getenv('MAIN_PROMO')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

TEXTS = {
    'ru': {
        'start': "💸 Приветствуем тебя!\n\nТы попал в закрытую систему, где сливаются рабочие алгоритмы ставок на 1Win.\nВсё, что ты здесь получишь — совершенно бесплатно.\n\nСледуй инструкции ниже и получай свою прибыль!",
        'choose_lang': "🌍 Пожалуйста, выберите язык:",
        'instructions': "📌 Инструкция:\n1. Перейди по ссылке и зарегистрируйся 👉 [Регистрация]({ref_link})\n2. Введи промокод: `{promo}`\n3. Пополни баланс на 1000₽\n\n⏰ *Алгоритм обновляется каждые 60 минут!*\nТоропитесь получить текущую рабочую версию!\n\nПосле выполнения всех шагов нажми кнопку '✅ Я выполнил(а)' 👇",
        'not_subscribed': "❌ Вы не подписались на канал.\nПожалуйста, подпишитесь и нажмите \"Проверить подписку ✅\"",
        'subscribe_first': "📢 Для доступа к боту необходимо подписаться на наш канал!",
        'help': "Ожидайте, с вами свяжется поддержка в ближайшее время.",
        'algorithm_sent': "🎰 Ваш алгоритм:",
        'admin_stats': "📊 Статистика:\n\n👥 Всего пользователей: {total_users}\n📢 Подписались: {subscribed_users}\n🎯 Нажали регистрацию: {clicked_registration}\n✅ Выполнили шаги: {completed_steps}\n📊 Получили алгоритм: {got_algorithm}\n\nЯзыки:\n{lang_stats}",
        'broadcast_sent': "✅ Рассылка отправлена {success} пользователям\n❌ Не удалось отправить: {failed}",
        'confirm_steps': "✅ Отлично! Теперь вы можете получить алгоритм 👇"
    },
    'en': {
        'start': "💸 Welcome!\n\nYou've entered a private system where working casino algorithms are leaked.\nEverything you get here is absolutely free.\n\nFollow the instructions below and start profiting!",
        'choose_lang': "🌍 Please choose your language:",
        'instructions': "📌 Instructions:\n1. Click the link and register 👉 [Registration]({ref_link})\n2. Enter promo code: `{promo}`\n3. Deposit $10\n\n⏰ *Algorithm updates every 60 minutes!*\nHurry up to get the current working version!\n\nAfter completing all steps, click the '✅ I have completed' button 👇",
        'not_subscribed': "❌ You are not subscribed to the channel.\nPlease subscribe and click \"Check subscription ✅\"",
        'subscribe_first': "📢 To access the bot, you need to subscribe to our channel!",
        'help': "Please wait, support will contact you shortly.",
        'algorithm_sent': "🎰 Your algorithm:",
        'admin_stats': "📊 Statistics:\n\n👥 Total users: {total_users}\n📢 Subscribed: {subscribed_users}\n🎯 Clicked registration: {clicked_registration}\n✅ Completed steps: {completed_steps}\n📊 Got algorithm: {got_algorithm}\n\nLanguages:\n{lang_stats}",
        'broadcast_sent': "✅ Broadcast sent to {success} users\n❌ Failed to send: {failed}",
        'confirm_steps': "✅ Great! Now you can get the algorithm 👇"
    }
}

# База данных
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
                clicked_registration INTEGER DEFAULT 0,
                completed_steps INTEGER DEFAULT 0,
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

async def update_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET language = ? WHERE user_id = ?',
            (language, user_id)
        )
        await db.commit()

async def update_subscription(user_id: int, status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET is_subscribed = ? WHERE user_id = ?',
            (1 if status else 0, user_id)
        )
        await db.commit()

async def update_clicked_registration(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET clicked_registration = 1 WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()

async def update_completed_steps(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET completed_steps = 1 WHERE user_id = ?',
            (user_id,)
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

async def get_user_data(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT is_subscribed, clicked_registration, completed_steps, got_algorithm FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            return [row[0] for row in await cursor.fetchall()]

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            total_users = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1') as cursor:
            subscribed_users = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT COUNT(*) FROM users WHERE clicked_registration = 1') as cursor:
            clicked_registration = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT COUNT(*) FROM users WHERE completed_steps = 1') as cursor:
            completed_steps = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT COUNT(*) FROM users WHERE got_algorithm = 1') as cursor:
            got_algorithm = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT language, COUNT(*) FROM users GROUP BY language') as cursor:
            lang_stats = await cursor.fetchall()
        
        return {
            'total_users': total_users,
            'subscribed_users': subscribed_users,
            'clicked_registration': clicked_registration,
            'completed_steps': completed_steps,
            'got_algorithm': got_algorithm,
            'lang_stats': lang_stats
        }

# Клавиатуры
def get_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
        ]
    ])

def get_subscribe_keyboard(lang: str):
    # Выбираем канал в зависимости от языка
    channel_username = CHANNEL_USERNAME_RU if lang == 'ru' else CHANNEL_USERNAME_EN
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 Подписаться на канал" if lang == 'ru' else "📢 Subscribe to channel", 
                url=f"https://t.me/{channel_username[1:]}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Проверить подписку" if lang == 'ru' else "✅ Check subscription", 
                callback_data="check_sub"
            )
        ]
    ])

def get_main_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎰 Регистрация в 1Win" if lang == 'ru' else "🎰 1Win Registration", 
                url=REF_LINK,
                callback_data="clicked_registration"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Я выполнил(а)" if lang == 'ru' else "✅ I have completed", 
                callback_data="confirm_steps"
            )
        ],
        [
            InlineKeyboardButton(
                text="📩 Нужна помощь" if lang == 'ru' else "📩 Need help", 
                callback_data="need_help"
            )
        ]
    ])

def get_algorithm_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Получить алгоритм" if lang == 'ru' else "📊 Get algorithm", 
                callback_data="get_algorithm"
            )
        ]
    ])

def get_admin_keyboard(lang: str):
    text = {
        'ru': {
            'stats': "📊 Статистика",
            'update': "🔄 Обновить алгоритм",
            'broadcast': "📢 Рассылка"
        },
        'en': {
            'stats': "📊 Statistics",
            'update': "🔄 Update algorithm",
            'broadcast': "📢 Broadcast"
        }
    }
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text[lang]['stats'], callback_data="admin_stats")],
        [InlineKeyboardButton(text=text[lang]['update'], callback_data="update_algorithm")],
        [InlineKeyboardButton(text=text[lang]['broadcast'], callback_data="admin_broadcast")]
    ])

# Состояния для админки
class AlgorithmUpdate(StatesGroup):
    waiting_for_image = State()
    waiting_for_text = State()

class BroadcastState(StatesGroup):
    waiting_for_message = State()

# Основной бот
logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    os.makedirs('data/current_algorithm', exist_ok=True)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Обработчик /start
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username or ""
        
        # Добавляем пользователя с временным языком
        await add_user(user_id, username, 'ru')
        
        # Предлагаем выбрать язык
        await message.answer(
            TEXTS['ru']['choose_lang'],
            reply_markup=get_language_keyboard()
        )
    
    # Выбор языка
    @dp.callback_query(F.data.startswith("lang_"))
    async def choose_language(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        language = callback.data.split('_')[1]  # lang_ru -> ru
        
        await update_user_language(user_id, language)
        
        # Показываем сообщение о подписке
        await callback.message.edit_text(
            TEXTS[language]['subscribe_first'],
            reply_markup=get_subscribe_keyboard(language),
            disable_web_page_preview=True
        )
        await callback.answer()
    
    # Проверка подписки
    @dp.callback_query(F.data == "check_sub")
    async def check_subscription(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        language = await get_user_language(user_id)
        
        # Выбираем канал в зависимости от языка
        channel_id = CHANNEL_ID_RU if language == 'ru' else CHANNEL_ID_EN
        
        try:
            chat_member = await callback.bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            if chat_member.status in ["member", "administrator", "creator"]:
                await update_subscription(user_id, True)
                await callback.message.edit_text(
                    f"{TEXTS[language]['start']}\n\n{TEXTS[language]['instructions'].format(ref_link=REF_LINK, promo=MAIN_PROMO)}",
                    reply_markup=get_main_keyboard(language),
                    disable_web_page_preview=True,
                    parse_mode='Markdown'
                )
            else:
                await callback.answer(TEXTS[language]['not_subscribed'], show_alert=True)
                
        except Exception as e:
            print(f"Subscription check error: {e}")
            await callback.answer("Error checking subscription", show_alert=True)
    
    # Отслеживание нажатия на регистрацию
    @dp.callback_query(F.data == "clicked_registration")
    async def track_registration_click(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        await update_clicked_registration(user_id)
        await callback.answer()
    
    # Подтверждение выполнения шагов (БЕЗ ПРОВЕРКИ)
    @dp.callback_query(F.data == "confirm_steps")
    async def confirm_steps(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        language = await get_user_language(user_id)
        
        # Обновляем статус выполнения шагов
        await update_completed_steps(user_id)
        
        # Показываем кнопку получения алгоритма
        await callback.message.edit_reply_markup(
            reply_markup=get_algorithm_keyboard(language)
        )
        
        await callback.answer(TEXTS[language]['confirm_steps'])
    
    # Получение алгоритма - ОДНИМ СООБЩЕНИЕМ с таймером срочности (БЕЗ ПРОВЕРКИ)
    @dp.callback_query(F.data == "get_algorithm")
    async def send_algorithm(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        language = await get_user_language(user_id)
        
        await update_algorithm_status(user_id)
        
        image_path = "data/current_algorithm/image.jpg"
        text_path = "data/current_algorithm/text.txt"
        
        try:
            # Читаем текст алгоритма
            algorithm_text = "🚀 Default algorithm text\n\nUse this strategy for better results!" if language == 'en' else "🚀 Стандартный текст алгоритма\n\nИспользуйте эту стратегию для лучших результатов!"
            
            if os.path.exists(text_path):
                with open(text_path, 'r', encoding='utf-8') as f:
                    algorithm_text = f.read()
            
            # Добавляем таймер срочности (1 час)
            time_left = datetime.datetime.now() + datetime.timedelta(hours=1)
            
            if language == 'en':
                timer_text = f"⏰ **TIME SENSITIVE!**\nThis algorithm is valid until: {time_left.strftime('%H:%M:%S')}\n\n"
                full_text = f"🎰 **YOUR WINNING ALGORITHM** 🎰\n\n{timer_text}{algorithm_text}\n\n✅ *Tested and proven strategy*\n🔥 *High success rate*\n\n⚠️ *Hurry up! Algorithm updates in 1 hour!*"
            else:
                timer_text = f"⏰ **СРОЧНО!**\nАлгоритм действителен до: {time_left.strftime('%H:%M:%S')}\n\n"
                full_text = f"🎰 **ВАШ АЛГОРИТМ ПОБЕД** 🎰\n\n{timer_text}{algorithm_text}\n\n✅ *Проверенная стратегия*\n🔥 *Высокий процент успеха*\n\n⚠️ *Торопитесь! Алгоритм обновится через 1 час!*"
            
            # Отправляем ОДНИМ сообщением
            if os.path.exists(image_path):
                # Отправляем фото с текстом в подписи
                photo = FSInputFile(image_path)
                await callback.message.answer_photo(
                    photo=photo,
                    caption=full_text,
                    parse_mode='Markdown'
                )
            else:
                # Если нет фото, отправляем только текст
                await callback.message.answer(
                    full_text,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"Algorithm send error: {e}")
            error_text = "❌ Error sending algorithm. Please try again later." if language == 'en' else "❌ Ошибка отправки алгоритма. Попробуйте позже."
            await callback.answer(error_text, show_alert=True)
        
        await callback.answer()
    
    # Помощь
    @dp.callback_query(F.data == "need_help")
    async def need_help(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        language = await get_user_language(user_id)
        
        await callback.message.answer(TEXTS[language]['help'])
        await callback.answer()
    
    # Админ панель
    @dp.message(Command("admin"))
    async def cmd_admin(message: types.Message):
        if message.from_user.id not in ADMIN_IDS:
            return
        
        language = await get_user_language(message.from_user.id)
        
        await message.answer(
            "👨‍💻 Admin Panel" if language == 'en' else "👨‍💻 Панель администратора",
            reply_markup=get_admin_keyboard(language)
        )
    
    # Статистика
    @dp.callback_query(F.data == "admin_stats")
    async def show_stats(callback: types.CallbackQuery):
        if callback.from_user.id not in ADMIN_IDS:
            return
        
        stats = await get_stats()
        language = await get_user_language(callback.from_user.id)
        
        lang_stats_text = ""
        for lang, count in stats['lang_stats']:
            lang_name = "Русский" if lang == 'ru' else "English"
            lang_stats_text += f"{lang_name}: {count}\n"
        
        text = TEXTS[language]['admin_stats'].format(
            total_users=stats['total_users'],
            subscribed_users=stats['subscribed_users'],
            clicked_registration=stats['clicked_registration'],
            completed_steps=stats['completed_steps'],
            got_algorithm=stats['got_algorithm'],
            lang_stats=lang_stats_text
        )
        
        await callback.message.answer(text)
        await callback.answer()
    
    # Обновление алгоритма
    @dp.callback_query(F.data == "update_algorithm")
    async def update_algorithm_start(callback: types.CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            return
        
        language = await get_user_language(callback.from_user.id)
        text = "Send new algorithm image:" if language == 'en' else "Отправьте новое изображение алгоритма:"
        
        await callback.message.answer(text)
        await state.set_state(AlgorithmUpdate.waiting_for_image)
        await callback.answer()
    
    @dp.message(AlgorithmUpdate.waiting_for_image, F.photo)
    async def process_algorithm_image(message: types.Message, state: FSMContext):
        os.makedirs("data/current_algorithm", exist_ok=True)
        
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        
        await message.bot.download_file(file_path, "data/current_algorithm/image.jpg")
        
        language = await get_user_language(message.from_user.id)
        text = "Now send text for the algorithm (will be under the image):" if language == 'en' else "Теперь отправьте текст для алгоритма (будет под изображением):"
        
        await message.answer(text)
        await state.set_state(AlgorithmUpdate.waiting_for_text)
    
    @dp.message(AlgorithmUpdate.waiting_for_text, F.text)
    async def process_algorithm_text(message: types.Message, state: FSMContext):
        with open("data/current_algorithm/text.txt", 'w', encoding='utf-8') as f:
            f.write(message.text)
        
        language = await get_user_language(message.from_user.id)
        text = "Algorithm updated successfully!" if language == 'en' else "Алгоритм успешно обновлен!"
        
        await message.answer(text)
        await state.clear()
    
    # Рассылка
    @dp.callback_query(F.data == "admin_broadcast")
    async def start_broadcast(callback: types.CallbackQuery, state: FSMContext):
        if callback.from_user.id not in ADMIN_IDS:
            return
        
        language = await get_user_language(callback.from_user.id)
        text = "Send message for broadcast:" if language == 'en' else "Отправьте сообщение для рассылки:"
        
        await callback.message.answer(text)
        await state.set_state(BroadcastState.waiting_for_message)
        await callback.answer()
    
    @dp.message(BroadcastState.waiting_for_message)
    async def process_broadcast(message: types.Message, state: FSMContext):
        language = await get_user_language(message.from_user.id)
        users = await get_all_users()
        
        success = 0
        failed = 0
        
        for user_id in users:
            try:
                # Пытаемся отправить сообщение
                if message.photo:
                    await message.bot.send_photo(
                        chat_id=user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption if message.caption else ""
                    )
                elif message.video:
                    await message.bot.send_video(
                        chat_id=user_id,
                        video=message.video.file_id,
                        caption=message.caption if message.caption else ""
                    )
                else:
                    await message.bot.send_message(
                        chat_id=user_id,
                        text=message.text,
                        parse_mode='Markdown' if message.text and any(c in message.text for c in '*_`[') else None
                    )
                success += 1
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")
                failed += 1
            await asyncio.sleep(0.1)  # Чтобы не превысить лимиты Telegram
        
        # Отчет о рассылке
        result_text = TEXTS[language]['broadcast_sent'].format(
            success=success,
            failed=failed
        )
        
        await message.answer(result_text)
        await state.clear()
    
    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())