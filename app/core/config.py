from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    REDIS_URL : str

    class Config:
        env_file = ".env"

setting = Settings()