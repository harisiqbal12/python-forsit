import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AdminAPI"
    PROJECT_DESCRIPTION: str = "Assignment of forsit"
    VERSION: str = "0.0.1"
    PROJECT_AUDIENCE: str = "Forsit"

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    HTTP_MAX_ATTEMPTS: int = int(os.getenv("HTTP_MAX_ATTEMPTS"))
    HTTP_ATTEMPT_COOLDOWN: int = int(os.getenv("HTTP_ATTEMPT_COOLDOWN"))
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC_ORDER: str = os.getenv("KAFKA_TOPIC_ORDER")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID")
    REDIS_INCOMING_ORDER: str = os.getenv("REDIS_INCOMING_ORDER")
    REDIS_LOW_INVENTORY: str = os.getenv("REDIS_LOW_INVENTORY")
    KAFKA_TOPIC_SALES: str = os.getenv("KAFKA_TOPIC_SALES")
    REDIS_QUEUE_ORDER: str = os.getenv("REDIS_QUEUE_ORDER")

    class Config:
        env_file = ".env"


settings = Settings()
