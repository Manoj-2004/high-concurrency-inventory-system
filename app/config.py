from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_host: str = "localhost"
    redis_port: int = 6379
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()