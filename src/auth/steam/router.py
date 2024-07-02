from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from auth.steam.models import AuthData
from auth.steam.schemas import AuthDataResponseDTO
from auth.steam.service import SteamAuthService
from config import settings

import httpx
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

    auth_service = SteamAuthService(session, settings.STEAM_API_KEY)
    
    player = await auth_service.get_steam_user_data(steam_id)
    username = player["personaname"]

    await auth_service.save_auth_data(user_ip, steam_id, username)

    return {"status": "success"}

@router.get("/steam/search", response_model=List[AuthDataResponseDTO])
async def search_auth_data(query: str, session: AsyncSession = Depends(get_async_session)):
    return await SteamAuthService(session, settings.STEAM_API_KEY).search_auth_data(query)

@router.get("/auth_data", response_model=List[AuthDataResponseDTO])
async def get_auth_data(limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    return await SteamAuthService(session, settings.STEAM_API_KEY).get_auth_data(limit, offset)