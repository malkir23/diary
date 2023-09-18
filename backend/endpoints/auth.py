from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, status, Request
from backend.services.user import PasswordService, UserSerializers, UserService
from backend.models.users import UserLoginSchema, CreateUserSchema
from backend.services.oauth2 import create_token, set_auth_tokens, check_auth
from backend.quaries.users import Users
from fastapi.responses import RedirectResponse
from datetime import datetime
from backend.services.email import EmailService

router = APIRouter()


@router.post("/login")
async def login(payload: UserLoginSchema, Authorize: AuthJWT = Depends()) -> dict:
    # Check if the user exist
    user = await UserService.get_user_by_filter({"email": payload.email.lower()})

    # Check if user verified his email
    if not user["verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email address",
        )

    # Check if the password is valid
    if not PasswordService.verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    await set_auth_tokens(user["id"], Authorize)

    # Send both access
    return {"status": "success", "user": UserSerializers.embeddedUserResponse(user)}

@router.post("/refresh")
async def refresh(Aut: AuthJWT = Depends(), user: dict = Depends(check_auth)) -> dict:
    Aut.jwt_refresh_token_required()
    await set_auth_tokens(user["id"], Aut)
    return {"status": "success"}

@router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout( Aut: AuthJWT = Depends(), user: dict = Depends(check_auth)) -> dict:
    Aut.unset_jwt_cookies()
    return {"status": "success"}


@router.get("/verify_email/{token}")
async def verify_me(token: str, request: Request) -> RedirectResponse:
    filters = {"verification_code": token}

    update_fields = {
        "verification_code": None,
        "verified": True,
        "updated_at": datetime.now(),
    }
    return {"status": await Users.update(filters, update_fields)}


@router.post("/forgot_password")
async def forgot_password(request: Request, email: str) -> dict:
    verification_code = await create_token(email.lower())
    user = await UserService.get_user_by_filter({"email": email.lower()})

    update_fields =  {
        "verification_code": verification_code,
        "verified": False,
        "updated_at": datetime.now(),
    }
    user = Users.update({"email": email}, update_fields)

    await EmailService.verify_email(request, verification_code, user, "forgot")
    return {"status": "success"}


@router.post("/set_new_password/{token}", status_code=status.HTTP_202_ACCEPTED)
async def set_new_password(payload: CreateUserSchema, token: str) -> dict:
    # Compare password and password Confirm
    PasswordService.add_new_password(payload)

    await UserService.get_user_by_filter({"verification_code": token})

    update_fields = {
        "verification_code": None,
        "verified": True,
        "updated_at": datetime.now(),
        "password": payload.password,
    }
    await Users.update( {"verification_code": token}, update_fields)

    return {"status": "success"}

