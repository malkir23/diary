from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .settings.config import settings, CookieSettings
from .endpoints import auth, users, scraping, assets, modules, adjustments, logs , asset_extra_data
from fastapi_jwt_auth import AuthJWT
from app.db.base import Modules, Adjustment
from app.services.modules_mock_data import modules as mock_modules
from fastapi.responses import JSONResponse


@AuthJWT.load_config
def get_config():
    return CookieSettings()


app = FastAPI(dependencies=[Depends(AuthJWT)])
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:9090",
    "https://example.com",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
app.include_router(users.router, tags=["User"], prefix="/api/user")
app.include_router(scraping.router, tags=["Scraping"], prefix="/api/scraping")
app.include_router(assets.router, tags=["Assets"], prefix="/api/assets")
app.include_router(modules.router, tags=["ModulesRules"], prefix="/api/modules")
app.include_router(adjustments.router, tags=["Adjustments"], prefix="/api/adjustments")
app.include_router(logs.router, tags=["Logs"], prefix="/api/logs")
app.include_router(asset_extra_data.router, tags=["Asset Extra Data"], prefix="/api/asset_extra_data")


@app.exception_handler(RequestValidationError)
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
