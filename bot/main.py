import asyncio
from aiogram import Bot, Dispatcher
from config import config
from middleware import UserDataMiddleware, LoggingBotMiddleware, RateLimitMiddleware

from router import router
from logger import Logger


logger = Logger.getinstance()
bot = Bot(config.tg_token)
dp = Dispatcher()
dp.message.middleware(UserDataMiddleware())
dp.message.middleware(LoggingBotMiddleware())
dp.message.middleware(RateLimitMiddleware())


async def start() -> None:
    print("bot started")
    logger.info("bot started")
    try:
        dp.include_router(router)
        await dp.start_polling(bot)
    except:
        logger.info("bot closed")
        print("bot closed")


if __name__ == "__main__":
    asyncio.run(start())