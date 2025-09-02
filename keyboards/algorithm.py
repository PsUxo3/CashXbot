from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile

from config import TEXTS
from database import update_algorithm_status, get_user_language
import os

router = Router()

@router.callback_query(F.data == "get_algorithm")
async def send_algorithm(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = await get_user_language(user_id)
    
    await update_algorithm_status(user_id)
    
    image_path = "data/current_algorithm/image.jpg"
    text_path = "data/current_algorithm/text.txt"
    
    try:
        if os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await callback.message.answer_photo(photo)
        
        if os.path.exists(text_path):
            with open(text_path, 'r', encoding='utf-8') as f:
                algorithm_text = f.read()
            
            await callback.message.answer(
                f"{TEXTS[language]['algorithm_sent']}\n\n{algorithm_text}"
            )
        else:
            await callback.message.answer(
                f"{TEXTS[language]['algorithm_sent']}\n\nDefault algorithm text"
            )
            
    except Exception as e:
        print(f"Algorithm send error: {e}")
        await callback.answer("Error sending algorithm", show_alert=True)
    
    await callback.answer()