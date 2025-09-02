from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import TEXTS, REF_LINK, MAIN_PROMO
from database import add_user, get_user_language
from keyboards.main_kb import get_sub_check_keyboard, get_main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    
    user_lang = message.from_user.language_code
    language = 'ru' if user_lang in ['ru', 'uk'] else 'en'
    
    await add_user(user_id, username, language)
    
    await message.answer(
        TEXTS[language]['start'],
        reply_markup=get_sub_check_keyboard(language)
    )