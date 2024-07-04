from fastapi import HTTPException
from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from .models import Bot
from .schemas import BotCreateDTO, BotStatusDTO

logger = logging.getLogger(__name__)

class BotService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bot(self, bot: BotCreateDTO):
        try:
            stmt = insert(Bot).values(
                steamid=bot.steamid,
                login=bot.login,
                password=bot.password,
                shared_secret=bot.shared_secret
            ).returning(Bot.id)

            result = await self.session.execute(stmt)
            bot_id = result.scalar_one()
            await self.session.commit()

            return bot_id

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def delete_bot(self, bot_id: int):
        try:
            stmt = delete(Bot).where(Bot.id == bot_id)
            await self.session.execute(stmt)
            await self.session.commit()

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def check_bot_status(self, bot_id: int):
        try:
            stmt = select(Bot.status).where(Bot.id == bot_id)
            result = await self.session.execute(stmt)
            status = result.scalar_one_or_none()

            if status is None:
                raise HTTPException(status_code=404, detail="Bot not found")

            return BotStatusDTO(status=status)

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
