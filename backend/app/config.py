import os


class BaseConfig:
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/cufinder")
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-insecure-change-me")
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    JSON_SORT_KEYS = False


class DevConfig(BaseConfig):
    DEBUG = True


class ProdConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


def get_config() -> type[BaseConfig]:
    env = os.environ.get("APP_ENV", "dev").lower()
    return ProdConfig if env == "prod" else DevConfig
