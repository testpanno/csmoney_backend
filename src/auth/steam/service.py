# services/auth_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import or_, insert
from auth.steam.models import AuthData
from auth.steam.schemas import AuthDataResponseDTO
from fastapi import HTTPException
import httpx
import logging

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
                AuthData.domain.contains(query)
            )
        )
        result = await self.session.execute(stmt)

        result_orm = result.scalars().all()

        result_dto = [AuthDataResponseDTO.model_validate(row, from_attributes=True) for row in result_orm]

        return result_dto
    
    async def save_auth_data(self, user_ip: str, steam_id: str, username: str):
        try:
            stmt = insert(AuthData).values(
                user_ip=user_ip,
                steam_id=steam_id,
                username=username,
                domain="csmoney"
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    async def get_auth_data(self, limit: int, offset: int):
        try:
            stmt = select(AuthData).limit(limit).offset(offset)
            result = await self.session.execute(stmt)

            result_orm = result.scalars().all()

            result_dto = [AuthDataResponseDTO.model_validate(row, from_attributes=True) for row in result_orm]

            return result_dto

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    @staticmethod
    def create_auth_url(redirect_uri):
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
    async def get_steam_user_data(steam_id: str, steam_api_key: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
                f"?key={steam_api_key}&steamids={steam_id}"
            )
            user_data = response.json()
            if not user_data["response"]["players"]:
                raise HTTPException(status_code=404, detail="User not found")
            return user_data["response"]["players"][0]


