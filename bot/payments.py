import uuid

from yookassa import Configuration, Payment, Webhook
from logger import Logger
from dotenv import load_dotenv
from typing import Literal
from config import payment_config, payment_config_test, config

load_dotenv()

logger = Logger.getinstance()


# Configuration.account_id = config.yookassa_shop_id
# Configuration.secret_key = config.yookassa_sk
Configuration.account_id = config.yookassa_shop_id_test
Configuration.secret_key = config.yookassa_sk_test

def create_payment(amount: int, username: str, chat_id: int, tariff_id: str, **extra):
    logger.info(f"create_payment")
    payment_id = str(uuid.uuid4())

    # Собираем метаданные
    metadata = {
        "username": username,
        "chat_id": chat_id,
        "tariff_type": tariff_id,
        **extra  # можно добавить всё, что хочешь
    }

    payment = Payment.create(
        payment_config_test(amount, **metadata),
        payment_id
    )

    logger.info(f"payment_data: {payment.confirmation.confirmation_url}")
    return payment.confirmation.confirmation_url, payment.id


def create_payment_test(amount: int, username: str, chat_id: int, tariff_id: str, **extra):
    logger.info(f"create_payment")
    payment_id = str(uuid.uuid4())

    # Собираем метаданные
    metadata = {
        "username": username,
        "chat_id": chat_id,
        "tariff_type": tariff_id,
        "payment_id": payment_id,
        **extra  # можно добавить всё, что хочешь
    }
    
    logger.warning(f"metadata: {metadata}")

    payment = Payment.create(
        payment_config_test(amount, **metadata),
        payment_id
    )

    logger.info(f"payment_data: {payment.confirmation.confirmation_url}")
    return payment.confirmation.confirmation_url, payment.id