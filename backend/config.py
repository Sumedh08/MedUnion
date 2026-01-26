import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Health System Decision Intelligence"
    API_V1_STR: str = "/api"
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    # Data Generation Settings
    SIMULATION_INTERVAL_SECONDS: int = 5
    
    class Config:
        case_sensitive = True

settings = Settings()
