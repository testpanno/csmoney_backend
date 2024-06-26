import uvicorn
from fastapi import FastAPI

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from auth.steam.router import router as steam_router


app = FastAPI(
    title="Trading app",
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(steam_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)