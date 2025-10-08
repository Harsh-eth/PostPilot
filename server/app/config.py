"""
Configuration management for PostPilot backend
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server configuration
    backend_port: int = 8787
    debug: bool = False
    
    # API configuration
    api_key_required: bool = False
    allowed_origins: str = "*"
    
    # LLM configuration
    fireworks_api_key: Optional[str] = None
    default_model: str = "accounts/sentientfoundation-serverless/models/dobby-mini-unhinged-plus-llama-3-1-8b"
    max_tokens: int = 500
    temperature: float = 0.7
    
    # Cache configuration
    use_redis: bool = False
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 86400  # 24 hours
    
    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window: int = 300  # 5 minutes
    
    # Database
    database_url: str = "sqlite:///./postpilot.db"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_allowed_origins(self) -> List[str]:
        """Get allowed origins as a list"""
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]
    
    @validator('fireworks_api_key')
    def validate_fireworks_key(cls, v):
        if v and len(v) < 10:
            raise ValueError('Fireworks API key appears to be invalid')
        return v


# Global settings instance
settings = Settings()
