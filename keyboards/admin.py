from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, TEXTS
from database import get_stats
from keyboards.main_kb import get_admin_keyboard
import os

router = Router()

class AlgorithmUpdate(StatesGroup):
    waiting_for_image = State()
    waiting_for_text = State()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    await message.answer(
        "👨‍💻 Admin Panel",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    stats = await get_stats()
    
    text = f"📊 Statistics:\n\n"
    text += f"Total Users: {stats['total_users']}\n"
    text += f"Got Algorithm: {stats['got_algorithm']}\n\n"
    text += "Language Stats:\n"
    
    for lang, count in stats['lang_stats']:
        text += f"{lang}: {count}\n"
    
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "update_algorithm")
async def update_algorithm_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    
    await callback.message.answer("Send new algorithm image:")
    await state.set_state(AlgorithmUpdate.waiting_for_image)
    await callback.answer()

@router.message(AlgorithmUpdate.waiting_for_image, F.photo)
async def process_algorithm_image(message: Message, state: FSMContext):
    os.makedirs("data/current_algorithm", exist_ok=True)
    
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    
    await message.bot.download_file(file_path, "data/current_algorithm/image.jpg")
    
    await message.answer("Now send algorithm text:")
    await state.set_state(AlgorithmUpdate.waiting_for_text)

@router.message(AlgorithmUpdate.waiting_for_text, F.text)
async def process_algorithm_text(message: Message, state: FSMContext):
    with open("data/current_algorithm/text.txt", 'w', encoding='utf-8') as f:
        f.write(message.text)
    
    await message.answer("Algorithm updated successfully!")
    await state.clear()