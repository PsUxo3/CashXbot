from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import TEXTS
from database import get_user_language

router = Router()

@router.callback_query(F.data == "need_help")
async def need_help(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = await get_user_language(user_id)
    
    await callback.message.answer(TEXTS[language]['help'])
    await callback.answer()