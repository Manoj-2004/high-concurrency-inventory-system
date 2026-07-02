from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_host: str = "localhost"
    redis_port: int = 6379
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    use_background_tasks: bool = False
    use_kafka: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_purchase_topic: str = "purchase-events"
    DLQ_topic = "purchase-events-dlq"
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()