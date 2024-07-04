
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from admin.logs.enums import ELogType

class LogCreateDTO(BaseModel):
    skins: dict
    status: ELogType
    offer_id: str
    target_steam_id: str
    bot_steam_id: str
    hold: Optional[datetime | None]


class LogResponseDTO(BaseModel):
    id: int
    created_at: datetime
    skins: dict
    status: ELogType
    offer_id: str
    target_steam_id: str
    bot_steam_id: str
    hold: Optional[datetime]

    class Config:
        from_attributes = True

