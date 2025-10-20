from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import config

sqlite_engine_str = "sqlite+aiosqlite:///berezka_vpn.db"
pg_engine_str = f"postgresql+asyncpg://{config.pg_login}:{config.pg_passw}@{config.pg_host}:{config.pg_port}/{config.pg_db_name}"
engine = create_async_engine(sqlite_engine_str)
local_session = async_sessionmaker(engine)

class Base(DeclarativeBase): pass

async def get_db():
    session = local_session()
    try:
        yield session
    finally:
        session.close()

