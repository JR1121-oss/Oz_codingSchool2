from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = "root"
    DB_PASSWORD: str = "password1234"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "ai_health"

    # JWT / 쿠키 설정 (.env 값이 있으면 그 값이 우선 적용됨)
    JWT_SECRET_KEY: str = "change-me-in-env"
    COOKIE_SECURE: bool = True

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
