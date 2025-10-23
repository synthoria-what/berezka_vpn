from data.db_core import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.inspection import inspect

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(index=True)
    telegram_chat_id: Mapped[int] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    subscription_url: Mapped[str] = mapped_column(index=True, default='None')
    users_invited: Mapped[int] = mapped_column(default=0)
    count_payed: Mapped[int] = mapped_column(default=0)
    role: Mapped[str] = mapped_column(default="user")
    
    def to_dict(self):
        """Безопасное преобразование ORM-объекта в dict"""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}