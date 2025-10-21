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

def create_payment(amount: int, chat_id: int, 
                   type_payment: str = "sbp"):
    logger.info(f"create_payment")
    payment_id = str(uuid.uuid4())
    if type_payment == "sbp":
        confirmation_type = "qr"

    payment = Payment.create(payment_config(
        amount, confirmation_type, 
        type_payment, chat_id, payment_id),payment_id
        )

    logger.info(f"payments_data: {payment.confirmation.confirmation_data}")
    return payment.confirmation.confirmation_data, payment.id


def create_payment_test(amount: int, chat_id: int, 
                        tariff_type: str = "first_tariff", type_payment: str = "sbp"):
    logger.info(f"create_payment")
    payment_id = str(uuid.uuid4())
    confirmation_type = "redirect"
    if type_payment == "sbp":
        confirmation_type = "qr"

    payment = Payment.create(payment_config_test(
        amount, confirmation_type,
         chat_id, payment_id,tariff_type),payment_id
        )

    logger.info(f"payments_data: {payment.confirmation.confirmation_url}")
    return payment.confirmation.confirmation_url, payment.id