#!/usr/bin/env python3
"""
Security utilities for MarketPulse Pro
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token (placeholder for demo)"""
    # In production, this would use JWT encoding
    return "demo_token_" + str(datetime.utcnow().timestamp())

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token (placeholder for demo)"""
    # In production, this would decode and validate JWT
    if token.startswith("demo_token_"):
        return {"sub": "demo_user"}
    return None
