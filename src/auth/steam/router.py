from fastapi import APIRouter, HTTPException, Request

from config import settings

import httpx
import logging

router = APIRouter(prefix="/auth")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/steam")
async def steam_login():
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
async def steam_callback(request: Request):
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

        # Fetch CS:GO inventory
        inventory_response = await client.get(
            f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=5000"
        )

        inventory_data = inventory_response.json()
        
        if 'assets' not in inventory_data or 'descriptions' not in inventory_data:
            raise HTTPException(status_code=404, detail="Inventory not found")

        # Parse inventory items
        inventory_items = []
        for asset in inventory_data['assets']:
            for description in inventory_data['descriptions']:
                if asset['classid'] == description['classid']:
                    inventory_items.append({
                        'name': description['name'],
                        'type': description['type'],
                        'market_hash_name': description['market_hash_name'],
                        'tradable': description['tradable'],
                        'marketable': description['marketable']
                    })


    return {
        "steam_id": steam_id,
        "username": username,
        "inventory": inventory_items
    }

