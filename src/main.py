import uvicorn
from fastapi import FastAPI

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from auth.steam.router import router as steam_router
from skin.router import router as skin_router
from admin.domains.router import router as admin_domains_router

app = FastAPI(
    title="Trading app",
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

app.include_router(steam_router)
app.include_router(skin_router)
app.include_router(admin_domains_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)