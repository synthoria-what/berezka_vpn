from fastapi import FastAPI, Request
from aiogram import Bot
from logger import Logger
from proxy_client import ProxyClient
from config import TariffConfig, config

app = FastAPI()
logger = Logger.getinstance()
bot = Bot(config.tg_token)
proxy_client = ProxyClient()
tariffs = TariffConfig()

@app.post("/webhook")
async def webhook(request: Request):
    logger.info("Сработал вебхук")
    data = await request.json()
    event = data.get("event")
    payment_object = data.get("object")
    metadata = payment_object.get("metadata")
    chat_id = metadata.get("chat_id")
    username = metadata.get("username")
    tariff_type = metadata.get("tariff_type")
    expire = metadata.get("expire_time")
    logger.info(f"data: {data}")
    logger.info(f"event: {event}")
    logger.info(f"metadata: {metadata}")
    logger.info(f"chat_id: {chat_id}")
    logger.info(f"username: {username}")
    logger.info(f"tariff_type: {tariff_type}")
    logger.info(f"expire_time: {expire}")
    if event == "payment.succeeded":
        logger.info("Вебхук подтвердил оплату")
        
        if tariff_type in tariffs.tariffs:
            logger.info(f"Подписка {tariff_type} нашлась в сервисе")
            try:
                # Получаем текущие данные пользователя
                user_info = await proxy_client.get_user(username)
                current_expire = expire

                # Генерируем конфиг с учётом старого expire
                config = tariffs.get_proxy_config(tariff_type, current_expire=current_expire)

                # Обновляем пользователя
                await proxy_client.edit_user(
                    username,
                    expire=config["expire"],
                    data_limit=config["data_limit"]
                )

                logger.info(f"Подписка {tariff_type} продлена до {config['expire']}")

            except Exception as e:
                logger.error(f"Ошибка при продлении подписки: {e}")
            await bot.send_message(int(chat_id), text='Подписка была успешно оплачена')
    else:
        logger.error("Оплата была отменена")
        await bot.send_message(int(chat_id), text='Произошла ошибка при оплате подписки')
        
    return {"status": 200}
        