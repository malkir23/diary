from pydantic import BaseSettings
from pydantic import BaseModel


class Settings(BaseSettings):
    POSTGRESQL_INITDB_ROOT_USERNAME: str
    POSTGRESQL_INITDB_ROOT_PASSWORD: str
    POSTGRESQL_INITDB_DATABASE: str
    POSTGRES_PORT: int

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    AUTHJWT_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    CLIENT_ORIGIN: str

    API_KEY: str

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
