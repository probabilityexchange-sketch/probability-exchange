#!/usr/bin/env python3
"""
Simplified configuration for demo mode
"""
import os
from typing import List

class Settings:
    """Simplified application settings for demo"""

    # Application
    app_name: str = os.getenv("APP_NAME", "MarketPulse Pro")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "demo_secret_key")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "demo_jwt_secret")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./demo.db")

    # CORS
    cors_origins: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    ).split(",")

    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    swagger_ui: bool = True
    docs_url: str = "/docs"

    # API Keys for external services
    KALSHI_API_KEY: str = os.getenv("KALSHI_API_KEY", "")
    POLYMARKET_API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")
    MANIFOLD_API_KEY: str = os.getenv("MANIFOLD_API_KEY", "")

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

# Global settings instance
settings = Settings()
