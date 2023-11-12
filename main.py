import asyncio
import logging

import check_handler
import common_handlers
import keyboard
import scammer_handlers
from config import config
from aiogram import Bot
from aiogram import Dispatcher, F
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hunderline
import db


bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()


async def load_db():
    await db.db_start()
    print("подключение к бд успешно!")

async def main():

    logging.basicConfig(level=logging.INFO)
    dp.include_router(check_handler.router)
    dp.include_router(common_handlers.router)
    dp.include_router(scammer_handlers.router)

    await load_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
