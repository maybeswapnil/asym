"""
Application configuration management.
"""

import os
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application settings
    app_name: str = Field(default="Python Boilerplate", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    app_description: str = Field(
        default="Production-ready Python boilerplate",
        env="APP_DESCRIPTION"
    )
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Database settings
    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=0, env="DATABASE_MAX_OVERFLOW")
    
    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_ssl: bool = Field(default=False, env="REDIS_SSL")
    
    # JWT settings
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_minutes: int = Field(
        default=10080,  # 7 days
        env="REFRESH_TOKEN_EXPIRE_MINUTES"
    )
    
    # CORS settings
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080,https://preview--cerebrum-challenge.lovable.app",
        env="ALLOWED_ORIGINS"
    )
    allowed_methods: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        env="ALLOWED_METHODS"
    )
    allowed_headers: str = Field(
        default="*",
        env="ALLOWED_HEADERS"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # External API settings
    external_api_base_url: str = Field(
        default="https://api.example.com",
        env="EXTERNAL_API_BASE_URL"
    )
    external_api_key: str = Field(default="your-api-key", env="EXTERNAL_API_KEY")
    external_api_timeout: int = Field(default=30, env="EXTERNAL_API_TIMEOUT")
    
    # Monitoring settings
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    
    # File upload settings
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: str = Field(
        default="image/jpeg,image/png,application/pdf",
        env="ALLOWED_FILE_TYPES"
    )
    
    # Helper properties for list parsing
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as list."""
        return [item.strip() for item in self.allowed_origins.split(',')]
    
    @property
    def allowed_methods_list(self) -> List[str]:
        """Get allowed methods as list."""
        return [item.strip() for item in self.allowed_methods.split(',')]
    
    @property
    def allowed_headers_list(self) -> List[str]:
        """Get allowed headers as list."""
        return [item.strip() for item in self.allowed_headers.split(',')]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as list."""
        return [item.strip() for item in self.allowed_file_types.split(',')]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
