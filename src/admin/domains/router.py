from fastapi import APIRouter, Depends
from .schemas import DomainResponse, DomainCreate, DomainUpdate
from .service import DomainService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_async_session
from auth.base_config import current_superuser

# All router are protected with superuser
router = APIRouter(
    prefix="/api/admin/domains",
    tags=["admin_domains"]
)

@router.post("/", response_model=DomainResponse, dependencies=[Depends(current_superuser)])
async def create_domain(domain_create: DomainCreate, session: AsyncSession = Depends(get_async_session)):
    return await DomainService(session).create_domain(domain_create)

@router.get("/{domain_id}", response_model=DomainResponse, dependencies=[Depends(current_superuser)])
async def get_domain(domain_id: int, session: AsyncSession = Depends(get_async_session)):
    return await DomainService(session).get_domain(domain_id)

@router.get("/", response_model=List[DomainResponse], dependencies=[Depends(current_superuser)])
async def get_domains(limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    return await DomainService(session).get_domains(limit, offset)

@router.put("/{domain_id}", response_model=DomainResponse, dependencies=[Depends(current_superuser)])
async def update_domain(domain_id: int, domain_update: DomainUpdate, session: AsyncSession = Depends(get_async_session)):
    return await DomainService(session).update_domain(domain_id, domain_update)

@router.delete("/{domain_id}", response_model=DomainResponse, dependencies=[Depends(current_superuser)])
async def delete_domain(domain_id: int, session: AsyncSession = Depends(get_async_session)):
    return await DomainService(session).delete_domain(domain_id)