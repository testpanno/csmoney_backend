from fastapi import HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from admin.logs.models import Log
from admin.logs.schemas import LogCreateDTO, LogResponseDTO
import logging

logger = logging.getLogger(__name__)

class LogService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_log(self, log: LogCreateDTO):
        try:
            stmt = insert(Log).values(
                skins=log.skins,
                status=log.status,
                target_steam_id=log.target_steam_id,
                bot_steam_id=log.bot_steam_id,
                hold=log.hold
            ).returning(Log.id)  # Return the ID of the inserted log

            result = await self.session.execute(stmt)
            log_id = result.scalar_one()  # Retrieve the ID from the result
            await self.session.commit()

            return log_id  # Return the created log ID
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await self.session.rollback()  # Rollback the session in case of error
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    async def get_all_logs(self, limit: int = 10, offset: int = 0):
        try:
            result = await self.session.execute(select(Log).limit(limit).offset(offset))
            result_orm = result.scalars().all()

            result_dto = [LogResponseDTO.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

