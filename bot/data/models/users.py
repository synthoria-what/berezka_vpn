from data.db_core import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(index=True)
    telegram_chat_id: Mapped[int] = mapped_column(index=True)
    role: Mapped[str] = mapped_column(default="user")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    ref_url: Mapped[str] = mapped_column()
    subscription_url: Mapped[str] = mapped_column(index=True)
    users_invited: Mapped[int] = mapped_column(default=0)
    count_payed: Mapped[int] = mapped_column(default=0)