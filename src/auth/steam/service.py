import httpx
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import asc, desc, or_, insert
from auth.steam.models import AuthData
from auth.steam.schemas import AuthDataCreateDTO, AuthDataResponseDTO
from fastapi import HTTPException
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from admin.domains.service import DomainService

logger = logging.getLogger(__name__)

class SteamAuthService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_auth_data(self, query: str):
        stmt = select(AuthData).where(
            or_(
                AuthData.steam_id.contains(query),
                AuthData.user_ip.contains(query),
                AuthData.username.contains(query),
            )
        )
        result = await self.session.execute(stmt)

        result_orm = result.scalars().all()

        result_dto = [AuthDataResponseDTO.model_validate(row, from_attributes=True) for row in result_orm]

        return result_dto
    
    async def save_auth_data(self, auth_data: AuthDataCreateDTO):
        try:
            stmt = insert(AuthData).values(
                user_ip=auth_data.user_ip,
                steam_id=auth_data.steam_id,
                username=auth_data.username,
                domain_id=auth_data.domain_id
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    # Тут связь с сервисом доменов чтобы получить имя по айди домена
    async def filter_auth_data(self, domain_id: int = None, username: str = None, steam_id: str = None, user_ip: str = None, limit: int = 10, offset: int = 0):
        try:
            query = select(AuthData)
            if domain_id:
                query = query.where(AuthData.domain_id == domain_id)
            if username:
                query = query.where(AuthData.username == username)
            if steam_id:
                query = query.where(AuthData.steam_id == steam_id)
            if user_ip:
                query = query.where(AuthData.user_ip == user_ip)
            
            query = query.order_by(desc(getattr(AuthData, "id"))).limit(limit).offset(offset)

            result = await self.session.execute(query)

            result_orm = result.scalars().all()

            # Get the unique domain IDs from the results
            domain_ids = {row.domain_id for row in result_orm}
            domain_map = {}
            
            # Fetch domain names for the unique domain IDs
            for domain_id in domain_ids:
                domain = await DomainService(self.session).get_domain(domain_id)
                if domain:
                    domain_map[domain_id] = domain.domain_name

            # Build the response DTOs
            result_dto = [
                AuthDataResponseDTO(
                    id=row.id,
                    user_ip=row.user_ip,
                    created_at=row.created_at,
                    steam_id=row.steam_id,
                    username=row.username,
                    domain_id=row.domain_id,
                    domain_name=domain_map.get(row.domain_id, "Unknown")
                )
                for row in result_orm
            ]

            return result_dto
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    @staticmethod
    def create_auth_url(redirect_uri):
        '''
            Function that creates steam oauth url. User will authenticate via this link, 
            and steam will redirect to our site, so there will be parsed his acc data
        '''
        auth_url = (
            f"https://steamcommunity.com/openid/login"
            f"?openid.ns=http://specs.openid.net/auth/2.0"
            f"&openid.mode=checkid_setup"
            f"&openid.return_to={redirect_uri}"
            f"&openid.realm={redirect_uri}"
            f"&openid.ns.sreg=http://openid.net/extensions/sreg/1.1"
            f"&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
            f"&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
        )
        return {"auth_url": auth_url}
    
    @staticmethod
    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5), retry=retry_if_exception_type(httpx.RequestError))
    async def get_steam_user_data(steam_id: str, steam_api_key: str):
        '''
            Function that parse account data by steamid64 and requires apikey
        '''
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
                    f"?key={steam_api_key}&steamids={steam_id}"
                )
                response.raise_for_status()
                user_data = response.json()
                if not user_data["response"]["players"]:
                    raise HTTPException(status_code=404, detail="User not found")
                return user_data["response"]["players"][0]
            except httpx.RequestError as exc:
                raise HTTPException(status_code=502, detail="Failed to fetch data from Steam API") from exc


