from datetime import datetime
from fastapi import Request, status, HTTPException, APIRouter, Depends
from app.db.base import Modules

from app.db.base import user_db
from app.models.users import CreateUserSchema, SetNewPassword, LoginUserSchema
from app.services.user import PasswordService, userSerializers
from app.services.email import EmailService
from app.services.oauth2 import create_token, set_auth_tokens, check_auth
from fastapi_jwt_auth import AuthJWT

router = APIRouter()


@router.post("/set_modules")
def set_modules():
    modules = Modules.find({})
    return {"result": True}
