from database import get_async_session

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from skin.schemas import SkinDTO
from skin.models import Skin
from skin.enums import ESkinExterior, ESkinPhase, ESkinRarity, ESkinType
from skin.helpers import apply_filters, apply_sorting

router = APIRouter(prefix="/api/skin", tags=["skins"])

@router.get("/", response_model=List[SkinDTO])
async def get_skins(
    db: AsyncSession = Depends(get_async_session),
    is_stattrak: Optional[bool] = Query(None, alias="isStatTrak"),
    limit: int = Query(10),
    offset: int = Query(0),
    order: str = Query("asc"),
    quality: Optional[ESkinExterior] = Query(None, alias="quality"),
    short_slug: Optional[str] = Query(None, alias="shortSlug"),
    sort: str = Query("price"),
    collection: Optional[str] = Query(None),
    phase: Optional[ESkinPhase] = Query(None),
    rarity: Optional[ESkinRarity] = Query(None),
    skin_type: Optional[ESkinType] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_float: Optional[float] = Query(None),
    max_float: Optional[float] = Query(None)
):
    query = select(Skin)

    # Apply filters
    query = apply_filters(
        query, Skin, is_stattrak, quality, short_slug, collection, phase, rarity, skin_type, min_price, max_price, min_float, max_float
    )
    
    # Apply sorting
    query = apply_sorting(query, Skin, sort, order)

    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)

    skins = result.scalars().all()

    return [SkinDTO.model_validate(skin, from_attributes=True) for skin in skins]
