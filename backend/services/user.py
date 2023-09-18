from passlib.context import CryptContext
from fastapi import status, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from functools import wraps
from backend.quaries.users import Users



class UserSerializers:
    @staticmethod
    def embeddedUserResponse(user: dict) -> dict:
        return {
            "id": user["id"],
            "name": user["username"],
            "email": user["email"],
        }


class UserService:
    @staticmethod
    async def get_user_by_filter(filter_fields: dict) -> bool:
        user = await Users.find_one(filter_fields)
        if not user:
            error_list = [key.replace('_', ' ').capitalize() for key in filter_fields.keys()]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incorrect {' '.join(error_list)}",
            )
        return user


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

