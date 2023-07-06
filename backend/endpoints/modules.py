from datetime import datetime
from fastapi import Request, status, HTTPException, APIRouter, Depends
from backend.db.base import Modules

from backend.db.base import user_db
from backend.models.users import CreateUserSchema, SetNewPassword, LoginUserSchema
from backend.services.user import PasswordService, userSerializers
from backend.services.email import EmailService
from backend.services.oauth2 import create_token, set_auth_tokens, check_auth
from fastapi_jwt_auth import AuthJWT

router = APIRouter()


@router.post("/set_modules")
def set_modules():
    modules = Modules.find({})
    return {"result": True}
