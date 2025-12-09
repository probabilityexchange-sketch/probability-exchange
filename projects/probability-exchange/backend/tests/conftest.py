"""
Pytest configuration and fixtures for MarketPulse Pro tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# Use simple test app instead of production app to avoid complex config
from fastapi import FastAPI
from app.api.v1 import api as v1_api

# Create test app
app = FastAPI(title="MarketPulse Pro Test API")
app.include_router(v1_api.api_router, prefix="/api/v1")
from api_client_integration import (
    PredictionMarketAggregator,
    APIConfig,
    MockMarketClient
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Create an async test client for the FastAPI app"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def mock_aggregator():
    """Create a mock prediction market aggregator for testing"""
    configs = {
        "polymarket": APIConfig(api_key="", base_url="https://gamma-api.polymarket.com"),
        "kalshi": APIConfig(api_key="", base_url="https://trading-api.kalshi.com/v2"),
        "manifold": APIConfig(api_key="", base_url="https://api.manifold.markets/v0"),
    }

    aggregator = PredictionMarketAggregator(configs)
    await aggregator.initialize_clients()

    yield aggregator

    await aggregator.cleanup()


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    from api_client_integration import MarketData
    from datetime import datetime

    return MarketData(
        id="test_market_1",
        platform="polymarket",
        question="Will this test pass?",
        description="A test market for unit tests",
        category="testing",
        market_type="binary",
        outcomes=["Yes", "No"],
        current_price=0.75,
        probability=0.75,
        volume_24h=10000,
        total_volume=100000,
        liquidity=50000,
        status="open",
        url="https://polymarket.com/test",
        last_updated=datetime.utcnow()
    )
