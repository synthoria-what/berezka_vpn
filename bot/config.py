import os
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
logger = Logger.getinstance()


class Config:
    def __init__(self,
                 tg_token: str,
                 pg_login: str,
                 pg_passw: str,
                 pg_port: str,
                 pg_host: str,
                 pg_db_name: str):
        self.tg_token = tg_token
        self.pg_login = pg_login
        self.pg_passw = pg_passw
        self.pg_port = pg_port
        self.pg_host = pg_host
        self.pg_db_name = pg_db_name


class SubPriceStars:
    def __init__(self):
        self.first_sub = 1 #45
        self.second_sub = 1 #100
        self.third_sub = 1 #150
        self.fourth_sub = 1 #200


class SubPriceRub:
    def __init__(self):
        self.first_sub = 89
        self.second_sub = 199
        self.third_sub = 359
        self.fourth_sub = 699


class SubDuration:
    def __init__(self):
        self.__day = 60 * 60 * 24
        self.month = self.__day * 30
        self.first_sub = self.month
        self.second_sub = self.month * 3
        self.third_sub = self.month * 6
        self.fourth_sub = self.month * 12

    def convert_to_days(self, duration: int) -> int:
        logger.info(f"convert from {duration}")
        day = int(duration / 30 / 60 / 60 / 24)
        logger.info(f"convert to {day}")
        return day



config = Config(
    tg_token=os.getenv("TG_TOKEN"),
    pg_login=os.getenv("PG_LOGIN"),
    pg_passw=os.getenv("PG_PASSW"),
    pg_port=os.getenv("PG_HOST"),
    pg_host=os.getenv("PG_PORT"),
    pg_db_name=os.getenv("PG_DB_NAME")
)