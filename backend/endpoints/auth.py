from datetime import datetime, date
from fastapi import Request, status, HTTPException, APIRouter, Depends, Response
from fastapi.responses import RedirectResponse

from backend.quaries.users import Users
from backend.models.users import CreateUserSchema
from backend.services.user import PasswordService, UserSerializers
from backend.services.email import EmailService
from backend.services.oauth2 import create_token, set_auth_tokens, check_auth
# from backend.services.url import create_url
# from fastapi_jwt_auth import AuthJWT

# from backend.services.utils import utc_now
# from backend.settings.config import settings

router = APIRouter()

@router.post("/all_users")
async def get_all_users() -> dict:
    return {"result": await Users.find()}

@router.post("/create_user")
async def create_user(payload: CreateUserSchema, request: Request) -> dict:
    # Check if user already exist
    print( payload.email.lower() )
    if await Users.find({"email": payload.email.lower()}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exist"
        )

    PasswordService.add_new_password(payload)

    token = await create_token(str(payload.email.lower()))
    user_data = payload.dict()
    # user_data["created_at"] = date.today()
    # user_data["updated_at"] = date.today()
    user_data["verification_code"] = token
    print(user_data)
    await Users.insert(user_data)
    # Compare password and password Confirm
    await EmailService.verify_email(request, token, user_data, "register")

    return {
        "status": "success",
        "message": "Verification token successfully sent to your email"
    }

