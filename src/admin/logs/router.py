from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from admin.logs.schemas import LogCreateDTO, LogResponseDTO
from admin.logs.service import LogService
from auth.base_config import current_superuser
from database import get_async_session

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
    