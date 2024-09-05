from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .settings.config import CookieSettings
from .endpoints import video, auth, users
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


@AuthJWT.load_config
def get_config():
    return CookieSettings()


backend = FastAPI(dependencies=[Depends(AuthJWT)])
origins = [
    # "http://localhost",
    # "http://localhost:5432",
    # "https://example.com",
    # "http://localhost:8000",
    "*"
]
backend.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend.mount("/static", StaticFiles(directory="backend/static"), name="static")

backend.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
backend.include_router(users.router, tags=["User"], prefix="/api/user")
backend.include_router(video.router, tags=["Video"], prefix="/api/video")


@backend.exception_handler(RequestValidationError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    msg = exc.errors()[0].get('msg')
    return JSONResponse(
        status_code=400,
        content={"error": msg}
    )
