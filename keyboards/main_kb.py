from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_sub_check_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Проверить подписку ✅" if lang == 'ru' else "Check subscription ✅", 
            callback_data="check_sub"
        )
    ]])

def get_main_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Получить алгоритм" if lang == 'ru' else "📊 Get algorithm", 
                callback_data="get_algorithm"
            )
        ],
        [
            InlineKeyboardButton(
                text="📩 Нужна помощь" if lang == 'ru' else "📩 Need help", 
                callback_data="need_help"
            )
        ]
    ])

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔄 Обновить алгоритм", callback_data="update_algorithm")]
    ])