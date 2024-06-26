from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from trade.enums import ETradeStatus, ETradeType, EGame

class TradeBase(BaseModel):
    user_id: int
    item_id: int
    trade_type: ETradeType
    status: ETradeStatus
    game: EGame

class TradeCreate(TradeBase):
    pass

class TradeUpdate(BaseModel):
    status: Optional[ETradeStatus] = None

class TradeInDBBase(TradeBase):
    id: int
    datetime: datetime

    class Config:
        orm_mode = True

class Trade(TradeInDBBase):
    pass

class TradeInDB(TradeInDBBase):
    pass