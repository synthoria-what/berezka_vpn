from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import config
from logger import Logger


logger = Logger.getinstance()
sqlite_engine_str = "sqlite+aiosqlite:///berezka_vpn.db"
pg_engine_str = f"postgresql+asyncpg://{config.pg_login}:{config.pg_passw}@{config.pg_host}:{config.pg_port}/{config.pg_db_name}"
engine = create_async_engine(pg_engine_str)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass


# Штука для FastAPI
async def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
        
async def init_db():
    logger.info("database init")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

