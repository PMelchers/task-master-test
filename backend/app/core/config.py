from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Scheduled Trader"
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite:///./scheduled_trader.db", env="DATABASE_URL")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-very-secret-key", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 8, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8084",
        ],
        env="CORS_ORIGINS"
    )
    
    # Environment settings
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Exchange settings
    MEXC_API_KEY: str = Field(default="", env="MEXC_API_KEY")
    MEXC_API_SECRET: str = Field(default="", env="MEXC_API_SECRET")
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()