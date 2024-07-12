from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthDataResponseDTO(BaseModel):
    id: int
    user_ip: str
    created_at: datetime
    steam_id: str
    username: str
    domain_id: int
    domain_name: str

    class Config:
        from_attributes = True

class AuthDataCreateDTO(BaseModel):
    user_ip: str
    steam_id: str
    username: str
    domain_id: int

