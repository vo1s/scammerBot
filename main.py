import asyncio
import logging

from handlers import check_handler, common_handlers, scammer_handlers, report_handler, empty_handler
from config import config
from aiogram import Bot
from aiogram import Dispatcher
import db
from middlewares.check_sub import CheckSubscription


async def load_db():
    await db.db_start()
    print("подключение к бд успешно!")

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()


async def main():
    # dp.message.middleware(AntiFloodMiddleware())
    dp.message.middleware(CheckSubscription())



    logging.basicConfig(level=logging.INFO)
    dp.include_router(common_handlers.router)
    dp.include_router(check_handler.router)
    dp.include_router(report_handler.router)
    dp.include_router(scammer_handlers.router)
    dp.include_router(empty_handler.router)

    await load_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
