from fastapi import APIRouter, status, HTTPException

from backend.services.assets import get_data_from_api
from backend.settings.config import settings
import requests
from backend.db.base import Data
from fastapi_jwt_auth import AuthJWT

router = APIRouter()
API_KEY = settings.API_KEY
ENDPOINT_SCRAPING = settings.ENDPOINT_SCRAPING
AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD


@AuthJWT.load_config
def get_config():
    return settings

#
# @router.get("/generate/")
# def generate():
#     get_data_from_api(period="w")  # weekly task
#     get_data_from_api(period="m")  # monthly task
#     get_data_from_api(period="d")  # daily task
#     return {"status": True}
