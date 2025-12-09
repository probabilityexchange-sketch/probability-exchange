#!/usr/bin/env python3
"""
Probex Consensus Dashboard Configuration

Central configuration management for the consensus dashboard
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ConsensusConfig:
    """Configuration for consensus dashboard"""
    
    # API Configuration
    POLYMARKET_API_KEY: str = os.getenv('POLYMARKET_API_KEY', '')
    KALSHI_API_KEY: str = os.getenv('KALSHI_API_KEY', '')
    MANIFOLD_API_KEY: str = os.getenv('MANIFOLD_API_KEY', '')
    
    # Data Sources
    ENABLED_SOURCES: List[str] = ['polymarket', 'kalshi', 'manifold']
    
    # Consensus Thresholds
    HIGH_CONSENSUS_THRESHOLD: float = 0.85
    MEDIUM_CONSENSUS_THRESHOLD: float = 0.70
    LOW_CONSENSUS_THRESHOLD: float = 0.50
    
    # Confidence Levels
    VERY_HIGH_CONFIDENCE: float = 0.90
    HIGH_CONFIDENCE: float = 0.75
    MEDIUM_CONFIDENCE: float = 0.60
    LOW_CONFIDENCE: float = 0.40
    
    # Rate Limiting
    POLYMARKET_RATE_LIMIT: int = 10  # requests per minute
    KALSHI_RATE_LIMIT: int = 60
    MANIFOLD_RATE_LIMIT: int = 100
    
    # Data Refresh
    DEFAULT_REFRESH_INTERVAL: int = 60  # seconds
    MAX_MARKETS_PER_SOURCE: int = 50
    
    # Categories
    DEFAULT_CATEGORIES: List[str] = [
        'politics', 'economy', 'technology', 'sports', 
        'entertainment', 'health', 'other'
    ]
    
    # UI Configuration
    DEFAULT_THEME: str = 'dark'
    PAGE_TITLE: str = 'Probex Consensus Dashboard'
    PAGE_ICON: str = '🎯'
    
    # Cache Configuration
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 300  # seconds (5 minutes)
    
    # Export Configuration
    EXPORT_FORMAT: str = 'json'
    INCLUDE_METADATA: bool = True
    
    # Risk Assessment
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4
    
    # Performance Monitoring
    ENABLE_METRICS: bool = True
    METRICS_EXPORT_INTERVAL: int = 3600  # seconds (1 hour)

class DevelopmentConfig(ConsensusConfig):
    """Development-specific configuration"""
    
    # Use simulated data in development
    USE_SIMULATED_DATA: bool = True
    
    # Lower rate limits for development
    POLYMARKET_RATE_LIMIT: int = 5
    KALSHI_RATE_LIMIT: int = 10
    MANIFOLD_RATE_LIMIT: int = 20
    
    # Faster refresh for development
    DEFAULT_REFRESH_INTERVAL: int = 30
    
    # Enable debug logging
    LOG_LEVEL: str = 'DEBUG'

class ProductionConfig(ConsensusConfig):
    """Production-specific configuration"""
    
    # Use real APIs in production
    USE_SIMULATED_DATA: bool = False
    
    # Production rate limits
    POLYMARKET_RATE_LIMIT: int = 10
    KALSHI_RATE_LIMIT: int = 60
    MANIFOLD_RATE_LIMIT: int = 100
    
    # Standard refresh interval
    DEFAULT_REFRESH_INTERVAL: int = 60
    
    # Production logging
    LOG_LEVEL: str = 'INFO'

def get_config() -> ConsensusConfig:
    """Get configuration based on environment"""
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    
    if environment == 'production':
        return ProductionConfig()
    elif environment == 'development':
        return DevelopmentConfig()
    else:
        return ConsensusConfig()

# API Endpoints Configuration
API_ENDPOINTS = {
    'polymarket': {
        'base_url': 'https://gamma-api.polymarket.com',
        'markets': '/markets',
        'categories': '/categories',
        'market_data': '/markets/{id}'
    },
    'kalshi': {
        'base_url': 'https://trading-api.kalshi.com/v2',
        'markets': '/markets',
        'categories': '/categories',
        'market_data': '/markets/{id}'
    },
    'manifold': {
        'base_url': 'https://api.manifold.markets/v0',
        'markets': '/markets',
        'categories': '/categories',
        'market_data': '/markets/{id}'
    }
}

# Color Scheme
COLORS = {
    'primary': '#00B3FF',
    'secondary': '#2EFFFA',
    'accent': '#FF3366',
    'success': '#22C55E',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'dark_bg': '#0a0f16',
    'surface': '#141b26',
    'text': '#ffffff',
    'text_secondary': '#7a8a99'
}

# Platform Colors
PLATFORM_COLORS = {
    'polymarket': COLORS['primary'],
    'kalshi': COLORS['secondary'],
    'manifold': COLORS['accent']
}

# Consensus Level Colors
CONSENSUS_COLORS = {
    'high': COLORS['success'],
    'medium': COLORS['warning'],
    'low': COLORS['danger']
}

# Signal Strength Colors
SIGNAL_COLORS = {
    'strong': COLORS['success'],
    'moderate': COLORS['warning'],
    'weak': COLORS['danger']
}