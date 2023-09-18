from datetime import datetime, date
from fastapi import Request, status, HTTPException, APIRouter, Depends, Response
from fastapi.responses import RedirectResponse

from backend.quaries.users import Users
from backend.models.users import CreateUserSchema
from backend.services.user import PasswordService, UserSerializers
from backend.services.email import EmailService
from backend.services.oauth2 import create_token, set_auth_tokens, check_auth


router = APIRouter()


@router.post("/all_users")
async def get_all_users(auth_user: dict = Depends(check_auth)) -> dict:
    users = await Users.find()
    serialized_users = [UserSerializers.embeddedUserResponse(user) for user in users]
    return {"result": serialized_users}


@router.post("/create_user")
async def create_user(
    payload: CreateUserSchema, request: Request, auth_user: dict = Depends(check_auth)
) -> dict:
    # Check if user already exist
    if await Users.find({"email": payload.email.lower()}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exist"
        )

    PasswordService.add_new_password(payload)

    token = await create_token(str(payload.email.lower()))
    user_data = payload.dict()
    user_data["verification_code"] = token

    await Users.insert(user_data)

    # Compare password and password Confirm
    await EmailService.verify_email(request, token, user_data, "register")

    return {
        "status": "success",
        "message": "Verification token successfully sent to your email",
    }
