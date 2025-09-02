from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import Bot

from config import CHANNEL_ID, TEXTS, REF_LINK, MAIN_PROMO
from database import update_subscription, get_user_language
from keyboards.main_kb import get_main_keyboard

router = Router()

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    language = await get_user_language(user_id)
    
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        if chat_member.status in ["member", "administrator", "creator"]:
            await update_subscription(user_id, True)
            await callback.message.edit_text(
                f"{TEXTS[language]['start']}\n\n{TEXTS[language]['instructions'].format(ref_link=REF_LINK, promo=MAIN_PROMO)}",
                reply_markup=get_main_keyboard(language),
                disable_web_page_preview=True
            )
        else:
            await callback.answer(TEXTS[language]['not_subscribed'], show_alert=True)
            
    except Exception as e:
        print(f"Subscription check error: {e}")
        await callback.answer("Error checking subscription", show_alert=True)