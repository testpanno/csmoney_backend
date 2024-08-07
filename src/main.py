import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from auth.steam.router import router as steam_router
from auth.router import router as custom_auth_router
from skin.router import router as skin_router
from admin.domains.router import router as admin_domains_router
from admin.logs.router import router as admin_logs_router
from admin.deposits.router import router as admin_deposits_router


app = FastAPI(
    title="Trading app",
)

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(custom_auth_router)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

app.include_router(steam_router)
app.include_router(skin_router)
app.include_router(admin_domains_router)
app.include_router(admin_logs_router)
app.include_router(admin_deposits_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=10000)