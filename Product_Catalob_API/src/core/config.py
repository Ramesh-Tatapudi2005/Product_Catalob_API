from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 3000
    mongo_uri: str
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"

settings = Settings()