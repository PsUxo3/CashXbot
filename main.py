import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers.start import router as start_router
from handlers.subscription import router as subscription_router
from handlers.algorithm import router as algorithm_router
from handlers.admin import router as admin_router
from handlers.common import router as common_router

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    
    import os
    os.makedirs('data/current_algorithm', exist_ok=True)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(start_router)
    dp.include_router(subscription_router)
    dp.include_router(algorithm_router)
    dp.include_router(admin_router)
    dp.include_router(common_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())