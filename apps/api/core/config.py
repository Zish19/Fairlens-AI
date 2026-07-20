from pydantic_settings import BaseSettings
from typing import List
from pydantic import AnyHttpUrl, Field, validator

class Settings(BaseSettings):
    # App config
    PROJECT_NAME: str = "FairLens AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Security & Auth
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and "*" in v:
            raise ValueError("CORS_ORIGINS cannot contain '*' in production")
        return v
    
    # Rate Limiting
    RATE_LIMIT_GLOBAL: str = "100/minute"
    RATE_LIMIT_UPLOAD: str = "5/minute"
    
    # Database
    DATABASE_URL: str = Field(..., min_length=1)
    
    # Background Jobs / Redis
    REDIS_URL: str = Field(..., min_length=1)
    
    # AI Provider
    AI_PROVIDER: str = Field(..., min_length=1)
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
