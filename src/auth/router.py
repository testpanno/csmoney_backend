# routes.py or main.py

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from auth.service import AuthService

router = APIRouter()

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str

@router.post("/api/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
):
    return await auth_service.login(form_data)

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/api/auth/refresh", tags=["auth"])
async def refresh_jwt_token(
    data: TokenRefreshRequest,
    auth_service: AuthService = Depends()
):
    return await auth_service.refresh_jwt_token(data.refresh_token)


