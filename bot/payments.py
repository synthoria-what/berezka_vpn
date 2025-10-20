import uuid
import os

from yookassa import Configuration, Payment
from logger import Logger
from dotenv import load_dotenv
from typing import Literal
from config import payment_config

load_dotenv()

logger = Logger.getinstance()

acc_id = os.getenv("YOOKASSA_SHOP_ID")
secret_key = os.getenv("YOOKASSA_SECRET_KEY")

# Configuration.account_id = acc_id
# Configuration.secret_key = secret_key
Configuration.account_id = "1041305"
Configuration.secret_key = "test_PNTvM-9eEgTUUfjT6PnevgVi3kkTQKWJ3zcEYs2FHm4"

def create_payment(amount: int, chat_id: int, 
                   type_payment: Literal["bank_card", "sbp"] = "bank_card"):
    logger.info(f"create_payment")
    payment_id = str(uuid.uuid4())
    if type_payment == "sbp":
        confirmation_type = "qr"
    else:
        confirmation_type = "redirect"

    # receipt = create_receipt(count, amount, payment_id, chat_id)

    payment = Payment.create(payment_config(amount, confirmation_type, 
                                            type_payment, chat_id, payment_id)
        ,payment_id)


    if type_payment == "sbp":
        logger.info(f"payments_data: {payment.confirmation.confirmation_data}")
        return payment.confirmation.confirmation_data, payment.id
    else:
        logger.info(f"payments_url: {payment.confirmation.confirmation_url}")
        return payment.confirmation.confirmation_url, payment.id