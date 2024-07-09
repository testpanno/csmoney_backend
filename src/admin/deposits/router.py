from fastapi import APIRouter, HTTPException, Depends
from .service import CryptoService
from auth.base_config import current_superuser

router = APIRouter(
    prefix="/api/admin/deposits",
    tags=["deposits"]
)

@router.get("/{crypto}/{address}", dependencies=[Depends(current_superuser)])
async def get_transactions(crypto: str, address: str):
    if crypto.lower() == "btc":
        return await CryptoService().get_btc_transactions(address)
    elif crypto.lower() == "eth":
        return await CryptoService().get_eth_transactions(address)
    elif crypto.lower() == "usdt-erc20":
        return await CryptoService().get_usdt_transactions(address)
    else:
        raise HTTPException(status_code=400, detail="Unsupported cryptocurrency")
