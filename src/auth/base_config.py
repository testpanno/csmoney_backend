# base_config.py

from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from fastapi_users import FastAPIUsers
from auth.manager import get_user_manager
from auth.models import User
from config import settings

# Access token configuration
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_AUTH, lifetime_seconds=3600) # 1 hour

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Refresh token configuration
refresh_bearer_transport = BearerTransport(tokenUrl="auth/jwt/refresh")

def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_AUTH, lifetime_seconds=2592000)  # 30 days

refresh_auth_backend = AuthenticationBackend(
    name="jwt-refresh",
    transport=refresh_bearer_transport,
    get_strategy=get_refresh_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend, refresh_auth_backend],
)

current_user = fastapi_users.current_user()
current_superuser = fastapi_users.current_user(active=True, superuser=True)
