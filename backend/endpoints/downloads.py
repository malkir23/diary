from fastapi import APIRouter, Response
from starlette.responses import FileResponse
from backend.settings.config import settings

router = APIRouter()


@router.get("/open_ssh", response_class=Response)
async def download_sh():
    file_name = "open_ssh.sh"
    file_path = f"{settings.STATIC_FILES_ROOT}{file_name}"
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )


@router.get("/elxnode", response_class=Response)
async def download_elxnode():
    file_name = "elxnode.sh"
    file_path = f"{settings.STATIC_FILES_ROOT}{file_name}"
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )


@router.get("/update_elxnode", response_class=Response)
async def download_update_elxnode():
    file_name = "update_elxnode.sh"
    file_path = f"{settings.STATIC_FILES_ROOT}{file_name}"
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )


@router.get("/update_ubuntu", response_class=Response)
async def download_update_ubuntu():
    file_name = "update_ubuntu.sh"
    file_path = f"{settings.STATIC_FILES_ROOT}{file_name}"
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )
