from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from admin.bots.enums import EBotStatus
from database import Base


class Bot(Base):
    __tablename__ = "bot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    status: Mapped[EBotStatus] = mapped_column(Enum(EBotStatus), default=EBotStatus.ACTIVE)
    steamid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    shared_secret: Mapped[str] = mapped_column(String, nullable=False)
