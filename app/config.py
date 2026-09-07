from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key: str
    groq_api_key: str
    
    class Confic:
        env_file = ".env"

settings = Settings()