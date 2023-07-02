from passlib.context import CryptContext
from fastapi import status, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from app.services.logs import LogsService, TYPES_LOGS
from functools import wraps
from app.db.base import user_db
from bson.objectid import ObjectId


class userSerializers:
    @staticmethod
    def userEntity(user: dict) -> dict:
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "is_admin": user["is_admin"],
            "verified": user["verified"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }

    @staticmethod
    def userResponseEntity(user: dict) -> dict:
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "is_admin": user["is_admin"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }

    @staticmethod
    def embeddedUserResponse(user: dict) -> dict:
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
        }


class PasswordService:
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str):
        return cls.PWD_CONTEXT.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed_password: str):
        return cls.PWD_CONTEXT.verify(password, hashed_password)

    @classmethod
    def add_new_password(cls, payload: BaseModel) -> BaseModel:
        # Compare password and password Confirm
        if payload.password != payload.passwordConfirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
            )
        #  Hash the password
        payload.password = PasswordService.hash_password(payload.password)
        del payload.passwordConfirm
        return payload


def get_action_role(function_name):
    match function_name:
        case "assign_role" | "update_user" | "update_password":
            action = "update"
        case _:
            action = "none"

    return action


def users_log(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_id = kwargs["user_id"]
        writer = kwargs["auth_user"]
        after_object = dict(kwargs["user"])
        action = get_action_role(func.__name__)
        fields = list(after_object.keys())
        select_fields = { "_id": 0 }
        select_fields.update({field: 1 for field in fields})
        before_user_data = user_db.find_one(
            {"_id": ObjectId(user_id)}, select_fields
        )

        result = await func(*args, **kwargs)

        LogsService(
            before_object=before_user_data,
            after_object=after_object,
            fields=fields,
            type_=TYPES_LOGS.USERS,
            action=action,
            obj=after_object,
            user_id=str(writer["id"]),
        )
        return result

    return wrapper
