from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from auth.steam.schemas import AuthDataResponseDTO, AuthDataCreateDTO
from auth.steam.service import SteamAuthService
from config import settings
from utils import debug_mode
from auth.base_config import current_superuser

import logging

from database import get_async_session

router = APIRouter(
    prefix="/api/auth",
    tags=["steam_auth"]
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@debug_mode
@router.get("/steam")
async def steam_login():
    return SteamAuthService.create_auth_url(settings.STEAM_REDIRECT_URI)

@debug_mode
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

    auth_data = AuthDataCreateDTO(user_ip=user_ip, steam_id=steam_id, username=username, domain_id=1)

    await SteamAuthService(session).save_auth_data(auth_data)

    return {"status": "success"}

@debug_mode
@router.get("/steam/search", response_model=List[AuthDataResponseDTO], dependencies=[Depends(current_superuser)])
async def search_auth_data(query: str, session: AsyncSession = Depends(get_async_session)):
    '''
        Search auth_data by 1 query string
    '''
    return await SteamAuthService(session).search_auth_data(query)

@debug_mode
@router.get("/steam/auth_data", response_model=List[AuthDataResponseDTO], dependencies=[Depends(current_superuser)])
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
    
@debug_mode
@router.post("/steam/auth_data")
async def create_auth_data(auth_data: AuthDataCreateDTO, session: AsyncSession = Depends(get_async_session)):
    '''
        Allows other sites to send info about registrations via Steam.
    '''
    
    await SteamAuthService(session).save_auth_data(auth_data)

    return {"status": "success"}