from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from skin.enums import ESkinExterior, ESkinPhase, ESkinRarity, ESkinType

class SkinDTO(BaseModel):
    id: int
    app_id: int
    asset_id: int
    collection: Optional[str]
    collection_info: Optional[dict]
    price: float
    float_value: float
    playside_blue: Optional[int]
    fade: Optional[int]
    is_souvenir: bool
    is_stattrak: bool
    has_nametag: bool
    full_name: str
    full_slug: str
    short_name: str
    short_slug: str
    img: str
    stickers: dict
    delivery_time: int
    color: str
    rarity: ESkinRarity
    collection: Optional[str]
    phase: Optional[ESkinPhase]
    pattern: Optional[int]
    skin_type: ESkinType
    exterior: ESkinExterior
    has_trade_lock: bool
    trade_lock: Optional[datetime]  # Adjust according to your needs
    user_id: int


