import os


_DEV_SECRET_FALLBACK = "dev-insecure-change-me"


class BaseConfig:
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/cufinder")
    SECRET_KEY = os.environ.get("SESSION_SECRET", _DEV_SECRET_FALLBACK)
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
    if env != "prod":
        return DevConfig
    secret = os.environ.get("SESSION_SECRET")
    if not secret or secret == _DEV_SECRET_FALLBACK:
        raise RuntimeError(
            "SESSION_SECRET must be set to a non-default value when APP_ENV=prod."
        )
    return ProdConfig
