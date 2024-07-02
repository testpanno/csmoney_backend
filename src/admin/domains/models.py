
from database import Base

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

class Domain(Base):
    __tablename__ = "domain"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
