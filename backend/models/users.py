from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserBaseSchema(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    email: str
    password: str

class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str


class UserUpdateSchema(UserBaseSchema):
    is_admin: Optional[bool]
    verified: Optional[bool]
    ruls: Optional[str]
    is_admin: bool | None = None

