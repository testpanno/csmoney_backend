from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import DECIMAL, and_, cast, insert, select, update, desc, extract, func
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
            accepted_logs = await self.filter_logs(status=ELogType.ACCEPTED, limit=10000)
            total_price = sum(float(log.total_price) for log in accepted_logs)
            return total_price
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def get_logs_last_6_months(self):
        try:
            # Calculate the first day of the current month and six months ago
            today = datetime.utcnow().replace(day=1)
            six_months_ago = (today - timedelta(days=1)).replace(day=1) - timedelta(days=150)

            # Generate the expected months in the format YYYY-MM
            months = [(today.year, today.month)]
            for _ in range(5):
                last_month = months[-1][1] - 1 or 12
                last_year = months[-1][0] - (1 if last_month == 12 else 0)
                months.append((last_year, last_month))

            months.reverse()  # Order from oldest to newest

            # Query for logs in the last six months
            stmt = (
                select(
                    extract('month', Log.created_at).label('month'),
                    extract('year', Log.created_at).label('year'),
                    func.sum(cast(Log.total_price, DECIMAL)).label('total_price')
                )
                .where(
                    and_(
                        Log.created_at >= six_months_ago,
                        Log.status == 'ACCEPTED'  # Adjust this line to match your status field
                    ))
                .group_by('year', 'month')
                .order_by('year', 'month')
            )
            result = await self.session.execute(stmt)
            stats = result.fetchall()

            # Create a dictionary with the query results
            stats_dict = {f"{int(row.year)}-{int(row.month):02d}": float(row.total_price) for row in stats}

            # Create the final result by merging with the expected months
            final_stats = []
            for year, month in months:
                month_str = f"{year}-{month:02d}"
                total_price = stats_dict.get(month_str, 0)
                final_stats.append({"month": month_str, "total_price": total_price})

            return final_stats

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def get_logs_last_month(self):
        try:
            # Calculate the first day of the current month
            first_day_of_current_month = datetime.utcnow().replace(day=1)

            # Convert total_price to numeric before summing
            stmt = (
                select(
                    func.sum(cast(Log.total_price, DECIMAL)).label('total_price')
                )
                .where(
                    and_(
                        Log.status == 'ACCEPTED',
                        Log.created_at >= first_day_of_current_month
                    )
                )
            )
            logger.debug(f"Executing query: {stmt}")
            result = await self.session.execute(stmt)
            total_price = result.scalar()
            return total_price
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await self.session.rollback()  # Rollback in case of error
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

