from pydantic import BaseSettings, EmailStr
from pydantic import BaseModel


class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME = "admin"
    MONGO_INITDB_ROOT_PASSWORD = "password123"
    MONGO_INITDB_DATABASE = "fuzzy_db"

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

    AVAILABLE_ASSETS: list = [
        ("AUD", 'AUD.FOREX'),
        ("BTC", 'BTC-USD.CC'),
        ("CHF", 'USDCHF.FOREX'),
        ("CNY", 'USDCNY.FOREX'),
        ("EEM", 'EEM.US'),
        ("EUR", 'EUR.Forex'),
        ("EWJ", 'EWJ.US'),
        ("EWY", 'EWY.US'),
        ("GBP", 'GBPUSD.FOREX'),
        ("GLD", 'GLD.US'),
        ("JPY", 'USDJPY.FOREX'),
        ("OIH", 'OIH.US'),
        ("OIL", 'XTI-USD.CC'),
        ("PDBC", 'PDBC.US'),
        ("QQQ", 'QQQ.US'),
        ("SLV", 'SLV.US'),
        ("SPY", 'SPY.US'),
        ("TLT", 'TLT.US'),
        ("USD", 'USD.Forex'),
        ("VNQ", 'VNQ.US'),
    ]
    AVAILABLE_PERIOD: list = ["m", "w", "d"]  # m=monthly , w=weekly , d=daily
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
