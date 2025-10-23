from typing import Annotated
from fastapi import FastAPI, Depends
from logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from data.models.users import User
from data.db_core import get_session

app = FastAPI()
logger = Logger.getinstance()

@app.get("/users/get_users")
async def get_users(session: Annotated[AsyncSession, Depends(get_session)]):
    users = await session.scalars(select(User))
    return {"users": users.all()}


@app.get("/users/user_exists")
async def user_exists(session: Annotated[AsyncSession, Depends(get_session)],
                      chat_id: int):
    user_exists = await session.scalar(select(exists().where(User.telegram_chat_id == chat_id)))
    session.close()
    return {"exists": user_exists}