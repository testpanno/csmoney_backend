from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from .models import Domain
from .schemas import DomainCreate, DomainUpdate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class DomainService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_domain(self, domain_create: DomainCreate):
        try:
            new_domain = Domain(domain_name=domain_create.domain_name)
            self.session.add(new_domain)
            await self.session.commit()
            await self.session.refresh(new_domain)
            return new_domain
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def get_domain(self, domain_id: int):
        result = await self.session.execute(select(Domain).where(Domain.id == domain_id))
        domain = result.scalar_one_or_none()
        if domain is None:
            raise HTTPException(status_code=404, detail="Domain not found")
        return domain

    async def get_domains(self, limit: int = 10, offset: int = 0):
        result = await self.session.execute(select(Domain).limit(limit).offset(offset))
        return result.scalars().all()

    async def update_domain(self, domain_id: int, domain_update: DomainUpdate):
        domain = await self.get_domain(domain_id)
        if domain:
            domain.domain_name = domain_update.domain_name
            await self.session.commit()
            await self.session.refresh(domain)
            return domain

    async def delete_domain(self, domain_id: int):
        domain = await self.get_domain(domain_id)
        if domain:
            await self.session.delete(domain)
            await self.session.commit()
            return domain
