from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class UserBaseSchema(BaseModel):
    name: str
    email: str
    is_admin: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class AssignRole(BaseModel):
    is_admin: bool = False


class SetNewPassword(BaseModel):
    password: constr(min_length=8)
    passwordConfirm: str


class UserUpdateSchema(BaseModel):
    name: Optional[str]
    email: Optional[str]
    is_admin: Optional[bool]
    verified: Optional[bool]
