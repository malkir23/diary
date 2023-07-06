from backend.db.base import user_db
from fastapi import HTTPException, status, Depends, APIRouter
from backend.models.users import AssignRole, UserUpdateSchema, SetNewPassword
from bson.objectid import ObjectId
from backend.services.oauth2 import check_auth, check_admin
from backend.services.user import userSerializers, PasswordService, users_log
from datetime import datetime

from backend.services.utils import utc_now

router = APIRouter()


@router.post("/assign_role/{user_id}")
@users_log
async def assign_role(
    user: AssignRole, user_id: str, is_admin: dict = Depends(check_admin),
    auth_user: dict = Depends(check_auth)
):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid id: {user_id}"
        )

    updated_user_data = user_db.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_admin": user.is_admin, "updated_at": utc_now()}}
    )
    if not updated_user_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong"
        )
    return {"status": "success", "message": "Role is updated successfully"}


@router.get("/get_all_user")
async def get_all_user(auth_user: dict = Depends(check_auth)):
    users = [userSerializers.userEntity(user) for user in user_db.find()]
    return {"status": "success", "users": users}


@router.get("/get_one_user/{user_id}")
async def get_one_user(user_id: str, auth_user: dict = Depends(check_auth)):
    user = userSerializers.userEntity(user_db.find_one({"_id": ObjectId(str(user_id))}))
    return {"status": "success", "user": user}


@router.post("/update_user/{user_id}")
@users_log
async def update_user(
    user: UserUpdateSchema, user_id: str, is_admin: dict = Depends(check_admin),
    auth_user: dict = Depends(check_auth)
) -> dict:
    user = {k: v for k, v in user.dict().items() if v is not None}
    user["updated_at"] = utc_now()
    user = user_db.find_one_and_update(
        {"_id": ObjectId(str(user_id))},
        {"$set": user},
        new=True,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid user id",
        )
    return {"status": "success"}


@router.post("/update_password/{user_id}", status_code=status.HTTP_202_ACCEPTED)
@users_log
async def set_new_password(
    user: SetNewPassword, user_id: str, is_admin: dict = Depends(check_admin),
    auth_user: dict = Depends(check_auth)
) -> dict:
    # Compare password and password Confirm
    PasswordService.add_new_password(user)
    user = user_db.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "verified": True,
                "updated_at": utc_now(),
                "password": user.password,
            }
        },
        new=True,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid user id",
        )

    return {"status": "success"}
