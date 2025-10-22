from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from data.models.users import User
from data.db_core import SessionLocal
from logger import Logger
from config import config

import uuid

logger = Logger.getinstance()

class SqlQueries:
    def __init__(self):
        self.session = SessionLocal()
        logger.info("session created")
    
    async def get_users(self):
        async with self.session as session:
            logger.info("sql, get_users")
            result = await session.execute(select(User))
            return result.scalars().all()
    
    async def create_user(self, username: str, tg_id: int, subscription_url: str|None=None):
        async with self.session as session:
            logger.info("sql, create_user")
            
            user = await session.scalar(select(User).where(User.telegram_chat_id == tg_id))
            if user:
                logger.info("sql, user found, return")
                return "Такой пользователь уже есть"
            ref_url = f"https://t.me/{config.bot_name}?start={uuid.uuid4()}"
            new_user = User(username=username, telegram_chat_id=tg_id, 
                            ref_url=ref_url, subscription_url=subscription_url)
            session.add(new_user)
            logger.info(f"sql, create_user: data, {new_user}")
            await session.commit()
            return "Пользотаель создан"
        
    async def delete_user(self, tg_id: int):
        async with self.session as session:
            logger.info("sql, delete_user")
            stmt = delete(User)

            if tg_id:
                stmt = stmt.where(User.telegram_chat_id == tg_id)
            else:
                raise ValueError("tg_id должен быть указан")

            await session.execute(stmt)
            await session.commit()

    
    async def get_user(self, tg_id: int) -> User:
        async with self.session as session:
            logger.info("sql, get_user")
            user = await session.scalar(select(User).where(User.telegram_chat_id == tg_id))
            if user:
                return user
            else:
                return None
            

    async def edit_user(self, tg_id: int, **kwargs) -> None:
        async with self.session as session:
            logger.info("sql, edit_user")
            user = await session.scalar(select(User).where(User.telegram_chat_id == tg_id))
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            await session.commit()