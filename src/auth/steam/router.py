from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from auth.steam.models import AuthData
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
    '''
        Function creates url for original steam auth
    '''
    auth_url = (
        f"https://steamcommunity.com/openid/login"
        f"?openid.ns=http://specs.openid.net/auth/2.0"
        f"&openid.mode=checkid_setup"
        f"&openid.return_to={settings.STEAM_REDIRECT_URI}"
        f"&openid.realm={settings.STEAM_REDIRECT_URI}"
        f"&openid.ns.sreg=http://openid.net/extensions/sreg/1.1"
        f"&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
        f"&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
    )
    return {"auth_url": auth_url}

@router.get("/steam/callback")
async def steam_callback(request: Request, session: AsyncSession = Depends(get_async_session)):
    '''
        Handles original steam auth, and saves auth data to database
    '''
    params = request.query_params
    logger.info(f"Received callback parameters: {params}")

    openid_claimed_id = params.get("openid.claimed_id")
    if not openid_claimed_id:
        raise HTTPException(status_code=400, detail="Missing openid.claimed_id parameter")

    steam_id = openid_claimed_id.split("/")[-1]
    
    async with httpx.AsyncClient() as client:
        # Fetch user summary
        response = await client.get(
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            f"?key={settings.STEAM_API_KEY}&steamids={steam_id}"
        )
        user_data = response.json()

        if not user_data["response"]["players"]:
            raise HTTPException(status_code=404, detail="User not found")

        player = user_data["response"]["players"][0]
        username = player["personaname"]

    user_ip = request.client.host

    stmt = insert(AuthData).values({
        "user_ip": user_ip,
        "steam_id": steam_id,
        "username": username,
        "domain": "csmoney"
    })

    await session.execute(stmt)

    await session.commit()

    return {"status": "success"}

