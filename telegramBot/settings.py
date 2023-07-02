from auth_data import db_settings


class Settings:
    @staticmethod
    def get_db_url() -> str:
        user = db_settings.get("user")
        password = db_settings.getenv('password')
        ip = db_settings("ip")
        db = db_settings("db")

        return f"{user}:{password}@{ip}/{db}"
