from datetime import datetime
from admin.logs.enums import ELogType
from database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import JSON, Enum, Integer, String, DateTime, func, ForeignKey

class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    skins: Mapped[dict] = mapped_column(JSON)
    status: Mapped[ELogType] = mapped_column(Enum(ELogType))
    target_steam_id: Mapped[str] = mapped_column(String)
    bot_steam_id: Mapped[str] = mapped_column(String)
    hold: Mapped[datetime | None] = mapped_column(DateTime)
    