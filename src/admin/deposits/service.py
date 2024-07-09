import os
import httpx
from fastapi import HTTPException
from config import settings

class CryptoService:
    def __init__(self):
        self.etherscan_api_key = settings.ETHERSCAN_API_KEY
        self.blockcypher_api_key = settings.BLOCKCYPHER_API_KEY
        self.etherscan_base_url = "https://api.etherscan.io/api"
        self.blockcypher_base_url = "https://api.blockcypher.com/v1/btc/main"

    async def get_btc_transactions(self, address: str):
        url = f"{self.blockcypher_base_url}/addrs/{address}/full"
        params = {"token": self.blockcypher_api_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching BTC transactions")

        data = response.json()
        return data

    async def get_eth_transactions(self, address: str):
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "asc",
            "apikey": self.etherscan_api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.etherscan_base_url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching ETH transactions")

        data = response.json()

        if data["status"] != "1":
            raise HTTPException(status_code=400, detail=data["message"])

        return data["result"]

    async def get_usdt_transactions(self, address: str):
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "asc",
            "apikey": self.etherscan_api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.etherscan_base_url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching USDT transactions")

        data = response.json()

        if data["status"] != "1":
            raise HTTPException(status_code=400, detail=data["message"])

        return data["result"]
