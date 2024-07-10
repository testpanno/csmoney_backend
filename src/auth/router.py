from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from auth.schemas import LoginRequest, LoginResponse, TokenRefreshRequest, TokenRequest
from auth.service import AuthService

router = APIRouter()



@router.post("/api/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(
    login_request: LoginRequest,
    auth_service: AuthService = Depends()
):
    tokens = await auth_service.login(login_request)

    return tokens


@router.post("/api/auth/refresh", tags=["auth"])
async def refresh_jwt_token(
    request: Request,
    auth_service: AuthService = Depends()
):
    refresh_token = request.cookies.get("refreshToken")
    return await auth_service.refresh_jwt_token(refresh_token)


@router.get("/api/auth/profile", tags=["auth"])
async def get_profile(
    request: Request,
    auth_service: AuthService = Depends()
):
    access_token = request.cookies.get("accessToken")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing"
        )
    
    user = await auth_service.get_user(access_token)
    return user

@router.post("/api/auth/logout", tags=["auth"])
async def logout(response: Response):
    response.delete_cookie("accessToken")
    response.delete_cookie("refreshToken")

    return {
        "message": "Logged out successfully",
        "currentCookie": response
    }