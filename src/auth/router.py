from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.base_config import get_refresh_jwt_strategy, get_jwt_strategy
from pydantic import BaseModel

from auth.manager import authenticate_user, get_user_manager

router = APIRouter()

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str

@router.post("/api/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager=Depends(get_user_manager)
):
    user = await authenticate_user(form_data, user_manager)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_strategy = get_jwt_strategy()
    refresh_strategy = get_refresh_jwt_strategy()

    access_token = await access_strategy.write_token(user)
    refresh_token = await refresh_strategy.write_token(user)

    return {"access_token": access_token, "refresh_token": refresh_token}

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/api/auth/refresh", tags=["auth"])
async def refresh_jwt_token(
    data: TokenRefreshRequest, 
    user_manager = Depends(get_user_manager)
):
    refresh_strategy = get_refresh_jwt_strategy()
    access_strategy = get_jwt_strategy()

    user = await refresh_strategy.read_token(data.refresh_token, user_manager)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    new_access_token = await access_strategy.write_token(user)

    return {"access_token": new_access_token}
    
    
    


