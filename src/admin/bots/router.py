from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import BotCreateDTO, BotResponseDTO, BotStatusDTO
from .service import BotService
from database import get_async_session

router = APIRouter(
    prefix="/api/admin/bots",
    tags=["bots"]
)

@router.post("/")
async def create_bot(bot: BotCreateDTO, session: AsyncSession = Depends(get_async_session)):
    return await BotService(session).create_bot(bot)
    
@router.delete("/{bot_id}")
async def delete_bot(bot_id: int, session: AsyncSession = Depends(get_async_session)):
    await BotService(session).delete_bot(bot_id)
    return {"status": "success"}

@router.get("/{bot_id}/status", response_model=BotStatusDTO)
async def check_bot_status(bot_id: int, session: AsyncSession = Depends(get_async_session)):
    return await BotService(session).check_bot_status(bot_id)
