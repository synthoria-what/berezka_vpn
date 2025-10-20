import os
from attr import dataclass
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
logger = Logger.getinstance()
from pydantic_settings import BaseSettings
from pydantic import Field

class Config(BaseSettings):
    tg_token: str
    pg_login: str
    pg_passw: str
    pg_port: str
    pg_host: str
    pg_db_name: str
    yookassa_sk: str = Field(alias="YOOKASSA_SECRET_KEY")
    yookassa_shop_id: str = Field(alias="YOOKASSA_SHOP_ID")
    yookassa_sk_test: str = Field(alias="YOOKASSA_SECRET_KEY_TEST")
    yookassa_shop_id_test: str = Field(alias="YOOKASSA_SHOP_ID_TEST")
    mb_username: str = Field(alias="MARZBAN_USERNAME")
    mb_passw: str = Field(alias="MARZBAN_PASSW")
    mb_api_url: str = Field(alias="MARZBAN_API_URL")

    class Config:
        env_file = ".env"


class SubPriceStars:
    def __init__(self):
        self.first_tariff = 1 #45
        self.second_tariff = 1 #100
        self.third_tariff = 1 #150
        self.fourth_tariff = 1 #200


class SubPriceRub:
    def __init__(self):
        self.first_tariff = 89
        self.second_tariff = 199
        self.third_tariff = 359
        self.fourth_tariff = 699


class SubDuration:
    def __init__(self):
        self.__day = 60 * 60 * 24
        self.month = self.__day * 30
        self.first_tariff = self.month
        self.second_tariff = self.month * 3
        self.third_tariff = self.month * 6
        self.fourth_tariff = self.month * 12

    def convert_to_days(self, duration: int) -> int:
        logger.info(f"convert from {duration}")
        day = int(duration / 30 / 60 / 60 / 24)
        logger.info(f"convert to {day}")
        return day

@dataclass
class Tariff:
    id: str
    name: str
    price_rub: int
    price_stars: int
    duration_seconds: int


class TariffConfig:
    DAY = 60 * 60 * 24
    MONTH = DAY * 30

    def __init__(self):
        self.tariffs = {
            "first_tariff": Tariff(
                id="first_tariff",
                name="1 месяц",
                price_rub=89,
                price_stars=1,
                duration_seconds=self.MONTH
            ),
            "second_tariff": Tariff(
                id="second_tariff",
                name="3 месяца",
                price_rub=199,
                price_stars=1,
                duration_seconds=self.MONTH * 3
            ),
            "third_tariff": Tariff(
                id="third_tariff",
                name="6 месяцев",
                price_rub=359,
                price_stars=1,
                duration_seconds=self.MONTH * 6
            ),
            "fourth_tariff": Tariff(
                id="fourth_tariff",
                name="12 месяцев",
                price_rub=699,
                price_stars=1,
                duration_seconds=self.MONTH * 12
            )
        }

    def get_days(self, seconds: int) -> int:
        return seconds // self.DAY

config = Config()


def payment_config(amount: int, confirmation_type: str, 
                   type_payment: str, chat_id: int, payment_id: int) -> dict:
    if type_payment == "sbp":
        config = {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": confirmation_type,
                    "return_url": "https://t.me/KittyVPN_bot",
                },
                "payment_method_data": {
                    "type": type_payment,
                },
                "capture": True,
                "description": "Оплата подписки на платные услуги телеграм бота",
                "metadata": {
                    "chat_id": str(chat_id),
                    "order_id": payment_id,
                }
            }
    else:
        config = {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": confirmation_type,
                    "return_url": "https://t.me/KittyVPN_bot",
                },
                "capture": True,
                "description": "Оплата подписки на платные услуги телеграм бота",
                "metadata": {
                    "chat_id": str(chat_id),
                    "order_id": payment_id,
                }
            }
        
    return config