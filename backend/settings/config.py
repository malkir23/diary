from pydantic import BaseSettings, EmailStr
from pydantic import BaseModel


class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE: str

    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    AUTHJWT_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    CLIENT_ORIGIN: str

    SENDGRID_API_KEY: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_FROM: EmailStr
    MAIL_FROM_NAME: str
    EMAILS_ERROR_SENDS_TO: str

    API_KEY: str
    ENDPOINT_SCRAPING: str
    CELERY_TEST_ENV: bool = True

    FRONT_PORT: int
    TESTING: bool

    class Config:
        env_file = "backend/.env"


settings = Settings()


class CookieSettings(BaseModel):
    authjwt_secret_key: str = settings.AUTHJWT_SECRET_KEY
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False
