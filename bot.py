import asyncio, logging, sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings
from database import init_db
from handlers import router
from services.poller import status_poller

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await init_db()
    bot = Bot(settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    poll_task = asyncio.create_task(status_poller(bot))
    try:
        await dp.start_polling(bot)
    finally:
        poll_task.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
