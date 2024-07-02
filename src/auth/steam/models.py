
from database import Base

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

class AuthData(Base):
    __tablename__ = "auth_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_ip: Mapped[str] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    steam_id: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String)
    domain: Mapped[str] = mapped_column(String)

    
