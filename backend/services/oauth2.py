from fastapi_jwt_auth import AuthJWT

from backend.services.utils import utc_now
from backend.settings.config import settings
from fastapi import Depends

from datetime import datetime, timedelta
from jose import jwt
from fastapi import status, HTTPException, Depends
from backend.db.base import user_db
from fastapi_jwt_auth import AuthJWT
from bson.objectid import ObjectId
from backend.services.user import userSerializers


async def set_auth_tokens(subject: str, Authorize: AuthJWT = Depends()) -> str:
    access_token = Authorize.create_access_token(
        subject=subject,
        expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN),
    )
    Authorize.set_access_cookies(access_token)

    refresh_token = Authorize.create_refresh_token(
        subject=subject,
        expires_time=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN),
    )
    Authorize.set_refresh_cookies(refresh_token)

    return access_token


async def create_token(id_: str) -> str:
    expire = utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    jwt_data = {"sub": id_, "exp": expire}
    return jwt.encode(jwt_data, settings.AUTHJWT_SECRET_KEY)


class NotVerified(Exception):
    pass


class UserNotFound(Exception):
    pass


def check_auth(Authorize: AuthJWT = Depends()) -> dict:
    """Checks if the user is logged in

    Returns:
        dict: Data about the user logged
    """
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = userSerializers.userEntity(
            user_db.find_one({"_id": ObjectId(str(user_id))})
        )

        if not user:
            raise UserNotFound("User no longer exist")

        if not user["verified"]:
            raise NotVerified("You are not verified")

    except Exception as e:
        match e.__class__.__name__:
            case "MissingTokenError":
                status_code = status.HTTP_401_UNAUTHORIZED
                detail = "You are not logged in"
            case "UserNotFound":
                status_code = status.HTTP_401_UNAUTHORIZED
                detail = "User no longer exist"
            case "NotVerified":
                status_code = status.HTTP_401_UNAUTHORIZED
                detail = "Please verify your account"
            case _:
                status_code = status.HTTP_401_UNAUTHORIZED
                detail = "Token is invalid or has expired"
        raise HTTPException(status_code=status_code, detail=detail)
    return user


def check_admin(
    Authorize: AuthJWT = Depends(), user: AuthJWT = Depends(check_auth)
) -> dict:
    if not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{user['name']} doesn't have enough rights",
        )
