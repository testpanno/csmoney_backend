from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from auth.steam.models import AuthData
from auth.steam.schemas import AuthDataResponseDTO
from auth.steam.service import SteamAuthService
from config import settings
from auth.base_config import current_superuser

import logging

from database import get_async_session

router = APIRouter(
    prefix="/api/auth",
    tags=["steam_auth"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/steam")
async def steam_login():
    return SteamAuthService.create_auth_url(settings.STEAM_REDIRECT_URI)

@router.get("/steam/callback")
async def steam_callback(request: Request, session: AsyncSession = Depends(get_async_session)):
    '''
        Handles original steam auth, and saves auth data to database
    '''
    params = request.query_params
    
    openid_claimed_id = params.get("openid.claimed_id")
    if not openid_claimed_id:
        raise HTTPException(status_code=400, detail="Missing openid.claimed_id parameter")

    steam_id = openid_claimed_id.split("/")[-1]
    user_ip = request.client.host

    player = await SteamAuthService.get_steam_user_data(steam_id, settings.STEAM_API_KEY)
    username = player["personaname"]

    await SteamAuthService(session).save_auth_data(user_ip, steam_id, username)

    return {"status": "success"}

@router.get("/steam/search", response_model=List[AuthDataResponseDTO])
async def search_auth_data(query: str, session: AsyncSession = Depends(get_async_session)):
    return await SteamAuthService(session).search_auth_data(query)

@router.get("/auth_data", response_model=List[AuthDataResponseDTO], dependencies=[Depends(current_superuser)])
async def filter_auth_data(
    domain_id: int = Query(None),
    username: str = Query(None),
    steam_id: str = Query(None),
    user_ip: str = Query(None),
    limit: int = Query(10),
    offset: int = Query(0),
    page: int = Query(1),
    session: AsyncSession = Depends(get_async_session)
):
    offset = (page - 1) * limit
    return await SteamAuthService(session).filter_auth_data(domain_id, username, steam_id, user_ip, limit, offset)