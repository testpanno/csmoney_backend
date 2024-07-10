from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict

class TokenRequest(BaseModel):
    accessToken: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)  # type: ignore

class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    role_id: int
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False

class UserUpdate(schemas.BaseUserUpdate):
    pass