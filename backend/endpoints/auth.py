from datetime import datetime
from fastapi import Request, status, HTTPException, APIRouter, Depends, Response
from fastapi.responses import RedirectResponse

from backend.db.base import user_db
from backend.models.users import CreateUserSchema, SetNewPassword, LoginUserSchema
from backend.services.user import PasswordService, userSerializers
from backend.services.email import EmailService
from backend.services.oauth2 import create_token, set_auth_tokens, check_auth
from backend.services.url import create_url
from fastapi_jwt_auth import AuthJWT

from backend.services.utils import utc_now
from backend.settings.config import settings

router = APIRouter()


@router.post("/login")
async def login(payload: LoginUserSchema, Authorize: AuthJWT = Depends()) -> dict:
    # Check if the user exist
    db_user = user_db.find_one({"email": payload.email.lower()})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect Email or Password",
        )
    user = userSerializers.userEntity(db_user)

    # Check if user verified his email
    if not db_user["verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email address",
        )

    # Check if the password is valid
    if not PasswordService.verify_password(payload.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    await set_auth_tokens(str(user["id"]), Authorize)

    # Send both access
    return {"status": "success", "user": user}


@router.post("/refresh")
async def refresh(Aut: AuthJWT = Depends(), user: dict = Depends(check_auth)) -> dict:
    Aut.jwt_refresh_token_required()
    await set_auth_tokens(str(user["id"]), Aut)
    return {"status": "success"}


@router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout(
    Authorize: AuthJWT = Depends(), user: dict = Depends(check_auth)
) -> dict:
    Authorize.unset_jwt_cookies()
    return {"status": "success"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUserSchema, request: Request) -> dict:
    # Check if user already exist
    if user_db.find_one({"email": payload.email.lower()}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exist"
        )
    # Compare password and password Confirm
    PasswordService.add_new_password(payload)

    token = await create_token(str(payload.email.lower()))

    payload.is_admin = False
    payload.verified = False
    payload.email = payload.email.lower()
    payload.created_at = utc_now()
    payload.updated_at = payload.created_at
    user_data = payload.dict()
    user_data["verification_code"] = token

    user_db.insert_one(user_data)
    await EmailService.verify_email(request, token, user_data, "register")

    return {
        "status": "success",
        "message": "Verification token successfully sent to your email",
    }


@router.get("/verify_email/{token}")
def verify_me(token: str, request: Request) -> RedirectResponse:
    status_code = status.HTTP_302_FOUND
    user_db.find_one_and_update(
        {"verification_code": token},
        {
            "$set": {
                "verification_code": None,
                "verified": True,
                "updated_at": utc_now(),
            }
        },
        new=True,
    )
    url = f"{create_url(request)}:{settings.FRONT_PORT}/login"
    return RedirectResponse(url=url, status_code=status_code)


@router.post("/forgot_password")
async def forgot_password(request: Request, email: str) -> dict:
    verification_code = await create_token(str(email.lower()))
    user = user_db.find_one_and_update(
        {"email": email},
        {
            "$set": {
                "verification_code": verification_code,
                "verified": False,
                "updated_at": utc_now(),
            }
        },
        new=True,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect Email",
        )
    await EmailService.verify_email(request, verification_code, user, "forgot")
    return {"status": "success"}


@router.post("/set_new_password/{token}", status_code=status.HTTP_202_ACCEPTED)
async def set_new_password(payload: SetNewPassword, token: str) -> dict:
    # Compare password and password Confirm
    PasswordService.add_new_password(payload)
    user = user_db.find_one_and_update(
        {"verification_code": token},
        {
            "$set": {
                "verification_code": None,
                "verified": True,
                "updated_at": utc_now(),
                "password": payload.password,
            }
        },
        new=True,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect token",
        )
    return {"status": "success"}
