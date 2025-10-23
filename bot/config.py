from datetime import datetime
import os
import time
from attr import dataclass
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
logger = Logger.getinstance()
from pydantic_settings import BaseSettings
from pydantic import Field

class Config(BaseSettings):
    tg_token: str
    bot_name: str
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
class UserResponseF:
    username: str
    status: str
    used_traffic: str
    sub_link: str
    created_at: str
    note: str

@dataclass
class Tariff:
    id: str
    name: str
    price_rub: int
    price_stars: int
    duration: int  # длительность в секундах (а не expire)
    data_limit: int = 0


class TariffConfig:
    """Универсальный конфиг тарифов для VPN-прокси и Telegram-подписок"""

    DAY = 60 * 60 * 24
    MONTH = DAY * 30

    def __init__(self):
        self.tariffs: dict[str, Tariff] = {
            "first_tariff": Tariff(
                id="first_tariff",
                name="1 месяц",
                price_rub=89,
                price_stars=1,
                duration=self.MONTH,
            ),
            "second_tariff": Tariff(
                id="second_tariff",
                name="3 месяца",
                price_rub=199,
                price_stars=3,
                duration=self.MONTH * 3,
            ),
            "third_tariff": Tariff(
                id="third_tariff",
                name="6 месяцев",
                price_rub=359,
                price_stars=6,
                duration=self.MONTH * 6,
            ),
            "fourth_tariff": Tariff(
                id="fourth_tariff",
                name="12 месяцев",
                price_rub=699,
                price_stars=12,
                duration=self.MONTH * 12,
            )
        }

    def get_proxy_config(self, tariff_id: str) -> dict:
        """Формирует конфиг для прокси: expire в Unix time"""
        tariff = self.tariffs[tariff_id]
        current_time = int(time.time())
        return {
            "expire": current_time + tariff.duration,
            "data_limit": tariff.data_limit
        }

    def get_subscription_config(self, tariff_id: str) -> dict:
        """Формирует конфиг для Telegram подписки"""
        tariff = self.tariffs[tariff_id]
        # Telegram поддерживает только 1 месяц
        return {
            "expire": self.MONTH,
            "price_stars": tariff.price_stars,
        }
        
    def get_days(self, duration: int) -> int:
        return duration // self.DAY

config = Config()


def payment_config(amount: int, **kwargs) -> dict:
    config = {
            "amount": {
                "value": str(amount),
                "currency": "RUB",
            },
            "confirmation": {
                "type": "qr",
                "return_url": "https://t.me/test_invite_send_bot",
            },
            "payment_method_data": {
                "type": "sbp",
            },
            "capture": True,
            "description": "Оплата подписки на платные услуги телеграм бота",
            "metadata": kwargs
        }
        
    return config


def payment_config_test(amount: int, **kwargs) -> dict:
    config = {
            "amount": {
                "value": str(amount),
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/test_invite_send_bot",
            },
            "capture": True,
            "description": "Оплата подписки на платные услуги телеграм бота",
            "metadata": kwargs,
        }
        
    return config