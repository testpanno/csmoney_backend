from typing import Optional

from fastapi import Depends, Request, HTTPException, status
from fastapi_users import (BaseUserManager, IntegerIDMixin, exceptions, models,
                           schemas)

from fastapi_users.exceptions import UserNotExists

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.password import PasswordHelper
from auth.models import User
from auth.utils import get_user_db
from config import settings


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_AUTH
    verification_token_secret = settings.SECRET_AUTH

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )

        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["role_id"] = 1

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


password_helper = PasswordHelper()

async def authenticate_user(
    email: str,
    password: str,
    user_manager: UserManager = Depends(get_user_manager)
) -> User:

    try:    
        user = await user_manager.get_by_email(email)
    except UserNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not password_helper.verify_and_update(password, user.hashed_password)[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return user