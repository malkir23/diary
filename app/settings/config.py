from pydantic import BaseSettings, EmailStr
from pydantic import BaseModel


class Settings(BaseSettings):
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

    AVAILABLE_ASSETS: list = ['AUD',
                              'BTC',
                              'CHF',
                              'CNY',
                              'DIA',
                              'EEM',
                              'EUR',
                              'EWJ',
                              'EWY',
                              'FXI',
                              'GBP',
                              'GLD',
                              'INDA',
                              'JPY',
                              'OIH',
                              'OIL',
                              'PDBC',
                              'QQQ',
                              'SLV',
                              'SPY',
                              'TLT',
                              'USD',
                              'VNQ']
    AVAILABLE_PERIOD: list = ["m", "w", "d"]  # m=monthly , w=weekly , d=daily
    API_KEY: str
    ENDPOINT_SCRAPING: str
    CELERY_TEST_ENV: bool = True

    FRONT_PORT: int
    TESTING: bool

    class Config:
        env_file = "app/.env"


settings = Settings()


class CookieSettings(BaseModel):
    authjwt_secret_key: str = settings.AUTHJWT_SECRET_KEY
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False
