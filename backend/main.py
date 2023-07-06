from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .settings.config import settings, CookieSettings
from .endpoints import auth, users, scraping, assets, modules, adjustments, logs , asset_extra_data
from fastapi_jwt_auth import AuthJWT
from backend.db.base import Modules, Adjustment
from backend.services.modules_mock_data import modules as mock_modules
from fastapi.responses import JSONResponse


@AuthJWT.load_config
def get_config():
    return CookieSettings()


backend = FastAPI(dependencies=[Depends(AuthJWT)])
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:9090",
    "https://example.com",
    "http://localhost:8000",
    "https://dev.d2xjxa21r0l1uv.amplifybackend.com/"
]
backend.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


backend.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
backend.include_router(users.router, tags=["User"], prefix="/api/user")
backend.include_router(scraping.router, tags=["Scraping"], prefix="/api/scraping")
backend.include_router(assets.router, tags=["Assets"], prefix="/api/assets")
backend.include_router(modules.router, tags=["ModulesRules"], prefix="/api/modules")
backend.include_router(adjustments.router, tags=["Adjustments"], prefix="/api/adjustments")
backend.include_router(logs.router, tags=["Logs"], prefix="/api/logs")
backend.include_router(asset_extra_data.router, tags=["Asset Extra Data"], prefix="/api/asset_extra_data")


@backend.exception_handler(RequestValidationError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    msg = exc.errors()[0].get('msg')
    return JSONResponse(
        status_code=400,
        content={"error": msg}
    )


def setup():
    def set_modules():
        Modules.delete_many({})
        Modules.insert_many(mock_modules)

    def set_adjustment():
        adjustment_config = {
            'name': 'basic',
            "buy_sell_percent": {"buy_plus": 1, "sell_minus": 1},
            "trend_values": {'1': 10, '2': 90},
            'assets': settings.AVAILABLE_ASSETS,
            'is_default': True,
            'sort_key': 0
        }
        adj = Adjustment.find_one({'is_default': True})
        if not adj:
            Adjustment.insert_one(adjustment_config)

    set_modules()
    set_adjustment()


setup()
