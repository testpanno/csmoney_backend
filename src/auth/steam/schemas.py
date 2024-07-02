from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthDataResponseDTO(BaseModel):
    id: int
    user_ip: str
    created_at: datetime
    steam_id: str
    username: str
    domain: str

    class Config:
        from_attributes = True
