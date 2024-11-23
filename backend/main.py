from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .settings.config import CookieSettings
from .endpoints import auth, users, downloads, u4u
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.db.base import init_db


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


# Список заблокованих IP
BLOCKED_IPS = {"78.153.140.224"}

@backend.middleware("http")
async def block_ips_middleware(request: Request, call_next):
    client_ip = request.client.host
    if client_ip in BLOCKED_IPS:
        raise HTTPException(status_code=403, detail="Access denied")
    return await call_next(request)


backend.mount("/static", StaticFiles(directory="backend/static"), name="static")


# backend.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
# backend.include_router(users.router, tags=["User"], prefix="/api/user")
backend.include_router(downloads.router, tags=["Downloads"], prefix="/api/downloads")
backend.include_router(u4u.router, tags=["Downloads"], prefix="/api/u4u")

@backend.exception_handler(RequestValidationError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    msg = exc.errors()[0].get('msg')
    return JSONResponse(
        status_code=400,
        content={"error": msg}
    )

@backend.on_event("startup")
async def startup_event():
    await init_db()
