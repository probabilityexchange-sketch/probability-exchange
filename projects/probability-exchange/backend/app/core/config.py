#!/usr/bin/env python3
"""
Configuration settings for MarketPulse Pro Backend

Environment-based configuration with validation and type safety.
"""

import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = Field(default="MarketPulse Pro", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, env="JWT_EXPIRE_MINUTES")  # 24 hours
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # API Keys
    polymarket_api_key: Optional[str] = Field(default=None, env="POLYMARKET_API_KEY")
    kalshi_api_key: Optional[str] = Field(default=None, env="KALSHI_API_KEY")
    manifold_api_key: Optional[str] = Field(default=None, env="MANIFOLD_API_KEY")
    
    # External Services
    stripe_publishable_key: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    coinbase_api_key: Optional[str] = Field(default=None, env="COINBASE_API_KEY")
    coinbase_api_secret: Optional[str] = Field(default=None, env="COINBASE_API_SECRET")
    
    plaid_client_id: Optional[str] = Field(default=None, env="PLAID_CLIENT_ID")
    plaid_secret: Optional[str] = Field(default=None, env="PLAID_SECRET")
    plaid_env: str = Field(default="sandbox", env="PLAID_ENV")
    
    # KYC Providers
    jumio_api_token: Optional[str] = Field(default=None, env="JUMIO_API_TOKEN")
    jumio_api_secret: Optional[str] = Field(default=None, env="JUMIO_API_SECRET")
    jumio_workflow_id: Optional[str] = Field(default=None, env="JUMIO_WORKFLOW_ID")
    
    onfido_api_token: Optional[str] = Field(default=None, env="ONFIDO_API_TOKEN")
    onfido_app_token: Optional[str] = Field(default=None, env="ONFIDO_APP_TOKEN")
    
    # Geo-location & VPN Detection
    ipgeolocation_api_key: Optional[str] = Field(default=None, env="IPGEOLOCATION_API_KEY")
    maxmind_account_id: Optional[str] = Field(default=None, env="MAXMIND_ACCOUNT_ID")
    maxmind_license_key: Optional[str] = Field(default=None, env="MAXMIND_LICENSE_KEY")
    
    # Email
    email_host: str = Field(default="localhost", env="EMAIL_HOST")
    email_port: int = Field(default=1025, env="EMAIL_PORT")
    email_username: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    email_password: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    email_use_tls: bool = Field(default=False, env="EMAIL_USE_TLS")
    email_from: str = Field(default="noreply@marketpulse.dev", env="EMAIL_FROM")
    
    # Monitoring & Logging
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Compliance Settings
    allowed_jurisdictions: List[str] = Field(default=["NV", "NJ", "DE"], env="ALLOWED_JURISDICTIONS")
    blocked_jurisdictions: List[str] = Field(default=["IL", "WA", "OR", "MT"], env="BLOCKED_JURISDICTIONS")
    min_age: int = Field(default=18, env="MIN_AGE")
    kyc_required_threshold: float = Field(default=1000.00, env="KYC_REQUIRED_THRESHOLD")
    
    # Risk Management
    max_bet_amount: float = Field(default=10000.00, env="MAX_BET_AMOUNT")
    max_daily_deposit: float = Field(default=50000.00, env="MAX_DAILY_DEPOSIT")
    max_withdrawal: float = Field(default=25000.00, env="MAX_WITHDRAWAL")
    commission_rate: float = Field(default=0.025, env="COMMISSION_RATE")  # 2.5%
    
    # Development Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    swagger_ui: bool = Field(default=True, env="SWAGGER_UI")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("allowed_jurisdictions", pre=True)
    def parse_allowed_jurisdictions(cls, v):
        """Parse allowed jurisdictions from string or list"""
        if isinstance(v, str):
            return [jurisdiction.strip() for jurisdiction in v.split(",")]
        return v
    
    @validator("blocked_jurisdictions", pre=True)
    def parse_blocked_jurisdictions(cls, v):
        """Parse blocked jurisdictions from string or list"""
        if isinstance(v, str):
            return [jurisdiction.strip() for jurisdiction in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"
    
    @property
    def allowed_jurisdictions_list(self) -> List[str]:
        """Get allowed jurisdictions as list"""
        return self.allowed_jurisdictions
    
    @property
    def blocked_jurisdictions_list(self) -> List[str]:
        """Get blocked jurisdictions as list"""
        return self.blocked_jurisdictions
    
    class Config:
        # Load from .env.example first, then override with .env if it exists
        env_file = (".env.example", ".env")
        case_sensitive = False
        extra = "ignore"
        # env_prefix = "MARKETPULSE_"

# Global settings instance
settings = Settings()