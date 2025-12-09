"""
Tests for API client integration
"""
import pytest
from datetime import datetime
from api_client_integration import (
    PredictionMarketAggregator,
    MockMarketClient,
    MarketData,
    OrderRequest,
    APIConfig
)


class TestMockMarketClient:
    """Test MockMarketClient functionality"""

    @pytest.mark.asyncio
    async def test_mock_client_get_markets(self):
        """Test MockMarketClient returns mock market data"""
        client = MockMarketClient("test_platform")
        markets = await client.get_markets(limit=5)

        assert isinstance(markets, list)
        assert len(markets) <= 5
        assert all(isinstance(m, MarketData) for m in markets)
        assert all(m.platform == "test_platform" for m in markets)

    @pytest.mark.asyncio
    async def test_mock_client_filter_by_category(self):
        """Test MockMarketClient category filtering"""
        client = MockMarketClient("test_platform")
        markets = await client.get_markets(category="crypto")

        assert all(m.category == "crypto" for m in markets)

    @pytest.mark.asyncio
    async def test_mock_client_get_specific_market(self):
        """Test MockMarketClient get specific market by ID"""
        client = MockMarketClient("test_platform")
        markets = await client.get_markets()

        if markets:
            market_id = markets[0].id
            market = await client.get_market(market_id)
            assert market is not None
            assert market.id == market_id

    @pytest.mark.asyncio
    async def test_mock_client_place_order(self):
        """Test MockMarketClient order placement"""
        client = MockMarketClient("test_platform")

        order = OrderRequest(
            market_id="test_market",
            outcome="Yes",
            order_type="buy",
            quantity=10,
            price=0.5
        )

        response = await client.place_order(order)

        assert response.success is True
        assert response.order_id is not None
        assert response.filled_quantity == order.quantity
        assert response.average_price == order.price


class TestPredictionMarketAggregator:
    """Test PredictionMarketAggregator functionality"""

    @pytest.mark.asyncio
    async def test_aggregator_initialization(self, mock_aggregator):
        """Test aggregator initializes with mock clients"""
        assert len(mock_aggregator.clients) > 0
        assert "polymarket" in mock_aggregator.clients
        assert "kalshi" in mock_aggregator.clients
        assert "manifold" in mock_aggregator.clients

    @pytest.mark.asyncio
    async def test_aggregator_get_all_markets(self, mock_aggregator):
        """Test fetching markets from all platforms"""
        markets = await mock_aggregator.get_all_markets(limit_per_platform=5)

        assert isinstance(markets, list)
        assert len(markets) > 0

        # Check we have markets from multiple platforms
        platforms = set(m.platform for m in markets)
        assert len(platforms) >= 1

    @pytest.mark.asyncio
    async def test_aggregator_markets_sorted_by_volume(self, mock_aggregator):
        """Test markets are sorted by 24h volume"""
        markets = await mock_aggregator.get_all_markets(limit_per_platform=10)

        if len(markets) > 1:
            # Check sorting (descending volume)
            for i in range(len(markets) - 1):
                assert markets[i].volume_24h >= markets[i + 1].volume_24h

    @pytest.mark.asyncio
    async def test_aggregator_compare_markets(self, mock_aggregator):
        """Test comparing markets across platforms"""
        question = "Will Bitcoin reach $100,000?"
        results = await mock_aggregator.compare_market(question)

        assert isinstance(results, dict)
        # At least some platforms should have results
        assert len(results) > 0


class TestAPIConfig:
    """Test APIConfig data class"""

    def test_api_config_defaults(self):
        """Test APIConfig has proper defaults"""
        config = APIConfig()

        assert config.api_key == ""
        assert config.secret_key is None
        assert config.base_url == ""
        assert config.rate_limit == 60
        assert config.timeout == 30
        assert config.retry_attempts == 3
        assert config.retry_delay == 1.0

    def test_api_config_custom_values(self):
        """Test APIConfig with custom values"""
        config = APIConfig(
            api_key="test_key",
            base_url="https://test.com",
            rate_limit=100,
            timeout=60
        )

        assert config.api_key == "test_key"
        assert config.base_url == "https://test.com"
        assert config.rate_limit == 100
        assert config.timeout == 60


class TestMarketData:
    """Test MarketData structure"""

    def test_market_data_creation(self, sample_market_data):
        """Test creating MarketData instance"""
        assert sample_market_data.id == "test_market_1"
        assert sample_market_data.platform == "polymarket"
        assert sample_market_data.question == "Will this test pass?"
        assert sample_market_data.probability == 0.75
        assert sample_market_data.status == "open"

    def test_market_data_with_minimal_fields(self):
        """Test MarketData with only required fields"""
        market = MarketData(
            id="minimal_market",
            platform="test",
            question="Test question?"
        )

        assert market.id == "minimal_market"
        assert market.platform == "test"
        assert market.question == "Test question?"
        # Check defaults
        assert market.market_type == "binary"
        assert market.volume_24h == 0.0
        assert market.status == "open"
