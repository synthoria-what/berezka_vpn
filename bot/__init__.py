from bot.config import Config
from dotenv import load_dotenv
import os

load_dotenv('.env')


config = Config(
    tg_token=os.getenv("TG_TOKEN"),
    pg_login=os.getenv("PG_LOGIN"),
    pg_passw=os.getenv("PG_PASSW"),
    pg_port=os.getenv("PG_HOST"),
    pg_host=os.getenv("PG_PORT"),
    pg_db_name=os.getenv("PG_DB_NAME")
)