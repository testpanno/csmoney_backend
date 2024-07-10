from fastapi import Depends, HTTPException, status
from auth.base_config import get_refresh_jwt_strategy, get_jwt_strategy
from auth.manager import get_user_manager, authenticate_user
from auth.schemas import LoginRequest

class AuthService:
    def __init__(self, user_manager=Depends(get_user_manager)):
        self.user_manager = user_manager
        self.access_strategy = get_jwt_strategy()
        self.refresh_strategy = get_refresh_jwt_strategy()

    async def login(self, login_request: LoginRequest):
        user = await authenticate_user(login_request.email, login_request.password, self.user_manager)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        access_token = await self.access_strategy.write_token(user)
        refresh_token = await self.refresh_strategy.write_token(user)

        return {"accessToken": access_token, "refreshToken": refresh_token}

    async def refresh_jwt_token(self, refresh_token: str):
        user = await self.refresh_strategy.read_token(refresh_token, self.user_manager)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        new_access_token = await self.access_strategy.write_token(user)
        return {"accessToken": new_access_token}
    
    async def get_user(self, access_token: str):
        user = await self.access_strategy.read_token(access_token, self.user_manager)

        return user
