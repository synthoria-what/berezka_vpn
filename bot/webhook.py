from fastapi import FastAPI, Request
from aiogram import Bot
from logger import Logger
from config import config

app = FastAPI()
logger = Logger.getinstance()
bot = Bot(config.tg_token)

@app.post("/webhook")
async def webhook(request: Request):
    logger.info("Сработал вебхук")
    data = await request.json()
    event = data.get("event")
    payment_object = data.get("object")
    metadata = payment_object.get("metadata")
    chat_id = metadata.get("chat_id")
    logger.info(f"data: {data}")
    logger.info(f"event: {event}")
    logger.info(f"metadata: {metadata}")
    logger.info(f"chat_id: {chat_id}")
    if event == "payment.succeeded":
        logger.info("Вебхук подтвердил оплату")
        await bot.send_message(int(chat_id), text='Подписка была успешно оплачена')
    else:
        logger.info("Оплата была отменена")
        await bot.send_message(chat_id, text='Произошла ошибка при оплате подписки')
        