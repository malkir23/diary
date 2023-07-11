from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .settings.config import CookieSettings
from .endpoints import auth, users
from fastapi_jwt_auth import AuthJWT
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


@backend.exception_handler(RequestValidationError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    msg = exc.errors()[0].get('msg')
    return JSONResponse(
        status_code=400,
        content={"error": msg}
    )
