from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Chat & Call Microservice"
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    REDIS_URL : str
    SECRET_KEY: str
    ALGORITHM: str




setting = Settings()