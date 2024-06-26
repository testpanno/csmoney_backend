from typing import List
from database import Base

from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, Enum, ForeignKey, DateTime, TIMESTAMP

from trade.enums import ETradeStatus, ETradeType, EGame

class Trade(Base):
    __tablename__ = 'trade'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    datetime: Mapped[TIMESTAMP] = mapped_column(DateTime, default=datetime.utcnow)
    trade_type: Mapped[ETradeType] = mapped_column(Enum(ETradeType))
    status: Mapped[ETradeStatus] = mapped_column(Enum(ETradeStatus))
    game: Mapped[EGame] = mapped_column(Enum(EGame))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    user = relationship("User")

    skins: Mapped[list["Skin"]] = relationship("Skin", back_populates="trades")
