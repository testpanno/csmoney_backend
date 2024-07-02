from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthDataCreateDTO(BaseModel):
    user_ip: str
    steam_id: str

class AuthDataResponseDTO(BaseModel):
    id: int
    user_ip: str
    created_at: datetime
    steam_id: str
    username: str

    class Config:
        from_attributes = True
