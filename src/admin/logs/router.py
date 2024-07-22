from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import Float
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from admin.logs.enums import ELogType
from admin.logs.schemas import LogCreateDTO, LogResponseDTO
from admin.logs.service import LogService
from auth.base_config import current_superuser
from database import get_async_session
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/api/admin/logs",
    tags=["logs"]
)

@router.post("/")
async def create_log(log: LogCreateDTO, session: AsyncSession = Depends(get_async_session)):
    log_id = await LogService(session).save_log(log)
    return {"id": log_id}


@router.get("/", response_model=List[LogResponseDTO], dependencies=[Depends(current_superuser)])
async def get_all_logs(
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_async_session)
):
    offset = (page - 1) * limit
    return await LogService(session).get_all_logs(limit, offset)


@router.get("/filter", response_model=List[LogResponseDTO], dependencies=[Depends(current_superuser)])
async def filter_logs(
    target_steam_id: str = Query(None),
    bot_steam_id: str = Query(None),
    status: ELogType = Query(None),
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_async_session)
):
    offset = (page - 1) * limit
    return await LogService(session).filter_logs(target_steam_id, bot_steam_id, status, limit, offset)

@router.get("/total_price", dependencies=[Depends(current_superuser)])
async def get_total_price_of_accepted_logs(session: AsyncSession = Depends(get_async_session)):
    try:
        total_price = await LogService(session).calculate_total_price_of_accepted_logs()
        return total_price
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail=f"Internal Server Error")\
    
@router.get("/stats/last_6_months")
async def get_stats_last_6_months(session: AsyncSession = Depends(get_async_session)):
    return await LogService(session).get_logs_last_6_months()

@router.get("/stats/last_month")
async def get_stats_last_month(session: AsyncSession = Depends(get_async_session)):
    return await LogService(session).get_logs_last_month()

