
from datetime import datetime
from pydantic import BaseModel

from admin.bots.enums import EBotStatus


class BotCreateDTO(BaseModel):
    steamid: str
    login: str
    password: str
    shared_secret: str

class BotResponseDTO(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    status: EBotStatus
    steamid: str
    login: str
    shared_secret: str

    class Config:
        from_attributes = True

class BotStatusDTO(BaseModel):
    status: EBotStatus