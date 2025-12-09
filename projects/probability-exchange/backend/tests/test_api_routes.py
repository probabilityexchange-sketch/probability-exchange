"""
Tests for API routes
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test health check and status endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint returns 200"""
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "marketpulse-api"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_api_status(self, async_client):
        """Test API status endpoint"""
        response = await async_client.get("/api/v1/status")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "operational"
        assert "platforms" in data
        assert "aggregator" in data
        assert "websocket" in data


class TestMarketEndpoints:
    """Test market data endpoints"""

    @pytest.mark.asyncio
    async def test_get_markets(self, async_client):
        """Test fetching markets from all platforms"""
        response = await async_client.get("/api/v1/markets")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "markets" in data
        assert "total" in data
        assert "timestamp" in data
        assert isinstance(data["markets"], list)

    @pytest.mark.asyncio
    async def test_get_markets_with_category(self, async_client):
        """Test fetching markets filtered by category"""
        response = await async_client.get("/api/v1/markets?category=crypto")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "markets" in data

        # All markets should be crypto category if any returned
        for market in data["markets"]:
            if market.get("category"):
                assert market["category"] == "crypto"

    @pytest.mark.asyncio
    async def test_get_markets_with_limit(self, async_client):
        """Test fetching markets with limit parameter"""
        limit = 10
        response = await async_client.get(f"/api/v1/markets?limit={limit}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data["markets"]) <= limit


class TestNewsEndpoints:
    """Test news API endpoints"""

    @pytest.mark.asyncio
    async def test_get_news(self, async_client):
        """Test fetching news articles"""
        response = await async_client.get("/api/v1/news?query=bitcoin&days_back=7")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "articles" in data
        assert "total" in data
        assert "timestamp" in data
        assert isinstance(data["articles"], list)

    @pytest.mark.asyncio
    async def test_get_news_invalid_days(self, async_client):
        """Test news endpoint with invalid days_back parameter"""
        response = await async_client.get("/api/v1/news?query=bitcoin&days_back=-1")
        # Should handle gracefully, either 400 or return empty
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
