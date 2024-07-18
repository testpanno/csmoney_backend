from fastapi import HTTPException
from sqlalchemy import and_, insert, select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from admin.logs.enums import ELogType
from admin.logs.models import Log
from admin.logs.schemas import LogCreateDTO, LogResponseDTO
import logging

from utils import get_log_total_price

logger = logging.getLogger(__name__)

class LogService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_log(self, log: LogCreateDTO):
        try:
            # Check if a log with the given offer_id already exists
            stmt_check = select(Log).where(Log.offer_id == log.offer_id)
            result_check = await self.session.execute(stmt_check)
            existing_log = result_check.scalar_one_or_none()

            if existing_log:
                # Update the status of the existing log to "new"
                stmt_update = update(Log).where(Log.offer_id == log.offer_id).values(status=log.status).returning(Log.id)
                result_update = await self.session.execute(stmt_update)
                log_id = result_update.scalar_one()  # Retrieve the ID from the result
                await self.session.commit()
                return log_id  # Return the updated log ID
            else:
                # Calculate the total price if skins are provided
                if log.skins:    
                    total_price = await get_log_total_price(log.skins)
                else:
                    total_price = 0

                # Insert the new log
                stmt_insert = insert(Log).values(
                    skins=log.skins,
                    total_price=total_price,
                    status=log.status,
                    offer_id=log.offer_id,
                    target_steam_id=log.target_steam_id,
                    bot_steam_id=log.bot_steam_id,
                    hold=log.hold
                ).returning(Log.id)  # Return the ID of the inserted log

                result_insert = await self.session.execute(stmt_insert)
                log_id = result_insert.scalar_one()  # Retrieve the ID from the result
                await self.session.commit()
                return log_id  # Return the created log ID

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await self.session.rollback()  # Rollback the session in case of error
            raise HTTPException(status_code=500, detail="Internal Server Error")
            
    async def get_all_logs(self, limit: int = 10, offset: int = 0):
        try:
            result = await self.session.execute(
                select(Log).order_by(desc(Log.created_at)).limit(limit).offset(offset)
            )
            result_orm = result.scalars().all()

            result_dto = [LogResponseDTO.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    async def filter_logs(self, target_steam_id: str = None, bot_steam_id: str = None, status: ELogType = None, limit: int = 10, offset: int = 0):
        try:
            filters = []
            if target_steam_id:
                filters.append(Log.target_steam_id.contains(target_steam_id))
            if bot_steam_id:
                filters.append(Log.bot_steam_id.contains(bot_steam_id))
            if status:
                filters.append(Log.status == status)
            
            stmt = select(Log).where(and_(*filters)).limit(limit).offset(offset)
            result = await self.session.execute(stmt)
            result_orm = result.scalars().all()

            result_dto = [LogResponseDTO.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    
    async def calculate_total_price_of_accepted_logs(self):
        try:
            accepted_logs = await self.filter_logs(status=ELogType.accepted, limit=10000)
            total_price = sum(log.total_price for log in accepted_logs)
            return total_price
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

