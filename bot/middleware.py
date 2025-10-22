import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from logger import Logger
from data.sql_queries import SqlQueries
from typing import Any, Dict, Callable, Awaitable

logger = Logger.getinstance()
sql_queries = SqlQueries()

    
class CancelHandler(Exception):
    """Событие обработки отменено (пользовательская реализация)"""
    pass


class LoggingBotMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any],
    ):
        if isinstance(event, Message):
            logger.info(f"Сообщение от пользователя {event.from_user.username} ({event.text})")
        else:
            logger.info(f"Пользователь нажал на инлайн кнопку. username: {event.from_user.username}, ({event.data})")
        return await handler(event, data)


class UserDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        tg_id = (
            event.message.chat.id
            if isinstance(event, CallbackQuery)
            else event.chat.id
        )

        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)

        user_data = await sql_queries.get_user(tg_id=tg_id)

        if user_data is None:
            msg = event.message if isinstance(event, CallbackQuery) else event
            await msg.answer("Пользователь не зарегистрирован. Пожалуйста, используйте /start.")
            raise CancelHandler()

        data["user_data"] = user_data
        return await handler(event, data)
    


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 5, period: int = 10):
        """
        :param limit: сколько сообщений можно за период
        :param period: период времени в секундах
        """
        self.limit = limit
        self.period = period
        self.users = {}  # {user_id: [timestamp1, timestamp2, ...]}

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ):
        user_id = event.from_user.id

        now = time.time()
        timestamps = self.users.get(user_id, [])

        # оставляем только те, что в пределах периода
        timestamps = [ts for ts in timestamps if now - ts < self.period]

        if len(timestamps) >= self.limit:
            await event.answer("Слишком часто! Попробуй через пару секунд ⏱️")
            return  # не вызываем хэндлер

        # добавляем текущее время
        timestamps.append(now)
        self.users[user_id] = timestamps

        return await handler(event, data)