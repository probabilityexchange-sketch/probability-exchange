#!/usr/bin/env python3
"""
API Integration Clients for MarketPulse Pro Prediction Markets

This module provides unified API clients for Polymarket, Kalshi, and Manifold
with consistent interfaces, error handling, and rate limiting. It also includes
a PredictionMarketAggregator to manage these clients and provide a unified
interface for fetching market data.
"""

import asyncio
import aiohttp
import time
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin
import hashlib
import hmac

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API clients"""
    api_key: str = ""
    secret_key: Optional[str] = None
    base_url: str = ""
    rate_limit: int = 60
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class MarketData:
    """Unified market data structure"""
    id: str
    platform: str
    question: str
    description: Optional[str] = None
    category: Optional[str] = None
    market_type: str = "binary"  # binary, multi_choice, scalar
    outcomes: Optional[List[str]] = None
    current_price: Optional[float] = None
    probability: Optional[float] = None
    volume_24h: float = 0.0
    total_volume: float = 0.0
    liquidity: float = 0.0
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    resolution_date: Optional[datetime] = None
    status: str = "open"
    url: Optional[str] = None
    last_updated: datetime = None

@dataclass
class OrderRequest:
    """Unified order request structure"""
    market_id: str
    outcome: str
    order_type: str = "buy"  # buy, sell
    quantity: int = 1
    price: Optional[float] = None  # If None, use market price
    time_in_force: str = "GTC"  # GTC, IOC, FOK

@dataclass
class OrderResponse:
    """Unified order response structure"""
    success: bool
    order_id: Optional[str] = None
    filled_quantity: int = 0
    average_price: Optional[float] = None
    total_cost: Optional[float] = None
    fees: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: datetime = None

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int, burst_limit: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.tokens = float(burst_limit)
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire a token for making a request"""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * (self.requests_per_minute / 60.0)
            
            if tokens_to_add > 0:
                self.tokens = min(float(self.burst_limit), self.tokens + tokens_to_add)
                self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            return False
    
    async def wait_for_token(self):
        """Wait until a token is available"""
        while not await self.acquire():
            await asyncio.sleep(0.1)  # Small sleep to prevent busy-waiting

class BaseAPIClient(ABC):
    """Base class for all prediction market API clients"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self._get_default_headers()
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        pass
    
    @abstractmethod
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get list of prediction markets"""
        pass
    
    @abstractmethod
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get details for a specific market"""
        pass
    
    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place an order on a market"""
        pass
    
    @abstractmethod
    async def get_user_balance(self) -> Dict[str, float]:
        """Get user's account balance"""
        pass
    
    @abstractmethod
    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get user's orders"""
        pass
        
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make a rate-limited API request with retry logic"""
        await self.rate_limiter.wait_for_token()
        
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.get('headers', {})
        headers.update(self._get_default_headers())
        kwargs['headers'] = headers
        
        for attempt in range(self.config.retry_attempts):
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                        headers=self._get_default_headers()
                    )

                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limit exceeded, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    response.raise_for_status() # Raise an exception for HTTP errors
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                logger.error(f"API Error ({self.__class__.__name__}) {e.status} for {url}: {e.message}")
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
            except aiohttp.ClientError as e:
                logger.error(f"Network or Client error ({self.__class__.__name__}) for {url}: {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
            except Exception as e:
                logger.error(f"Unexpected error ({self.__class__.__name__}) for {url}: {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        return {} # Should not be reached

    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response"""
        if not date_str:
            return None
        try:
            # Handle ISO 8601 with or without 'Z'
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except ValueError:
            logger.warning(f"Failed to parse datetime string: {date_str}")
            return None

    @staticmethod
    def _parse_timestamp(timestamp: Optional[Union[int, float]]) -> Optional[datetime]:
        """Parse Unix timestamp to datetime"""
        if timestamp is None:
            return None
        try:
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse timestamp: {timestamp}")
            return None


class MockMarketClient(BaseAPIClient):
    """Mock client that returns sample market data for demo purposes"""

    def __init__(self, platform: str):
        # Dummy config for mock client
        super().__init__(APIConfig(api_key="mock_key", base_url="mock_url"),)
        self.platform = platform
        logger.info(f"Initialized MockMarketClient for platform: {platform}")

    def _get_default_headers(self) -> Dict[str, str]:
        return {}

    async def get_markets(self, category: Optional[str] = None, limit: int = 50) -> List[MarketData]:
        """Return mock market data"""
        logger.info(f"MockMarketClient: Fetching markets for {self.platform}, category: {category}, limit: {limit}")
        mock_markets = [
            MarketData(
                id=f"{self.platform}_btc_100k",
                platform=self.platform,
                question="Will Bitcoin reach $100,000 by end of 2025?",
                description="Binary market on BTC price target",
                category="crypto",
                current_price=0.67,
                probability=0.67,
                volume_24h=125000,
                total_volume=2500000,
                liquidity=500000,
                status="open",
                url=f"https://{self.platform}.com/markets/btc-100k",
                last_updated=datetime.utcnow()
            ),
            MarketData(
                id=f"{self.platform}_eth_5k",
                platform=self.platform,
                question="Will Ethereum reach $5,000 by Q2 2025?",
                description="ETH price prediction market",
                category="crypto",
                current_price=0.45,
                probability=0.45,
                volume_24h=85000,
                total_volume=1200000,
                liquidity=300000,
                status="open",
                url=f"https://{self.platform}.com/markets/eth-5k",
                last_updated=datetime.utcnow()
            ),
            MarketData(
                id=f"{self.platform}_election",
                platform=self.platform,
                question="2024 Presidential Election Winner",
                description="Who will win the 2024 US Presidential Election?",
                category="politics",
                current_price=0.52,
                probability=0.52,
                volume_24h=450000,
                total_volume=8500000,
                liquidity=1200000,
                status="open",
                url=f"https://{self.platform}.com/markets/election-2024",
                last_updated=datetime.utcnow()
            ),
            MarketData(
                id=f"{self.platform}_ai_agi",
                platform=self.platform,
                question="Will AGI be achieved by 2027?",
                description="General artificial intelligence development timeline",
                category="technology",
                current_price=0.23,
                probability=0.23,
                volume_24h=95000,
                total_volume=1500000,
                liquidity=400000,
                status="open",
                url=f"https://{self.platform}.com/markets/agi-2027",
                last_updated=datetime.utcnow()
            ),
            MarketData(
                id=f"{self.platform}_climate",
                platform=self.platform,
                question="Will global temperature rise exceed 1.5°C by 2030?",
                description="Climate change prediction market",
                category="climate",
                current_price=0.78,
                probability=0.78,
                volume_24h=65000,
                total_volume=950000,
                liquidity=250000,
                status="open",
                url=f"https://{self.platform}.com/markets/climate-1-5c",
                last_updated=datetime.utcnow()
            )
        ]

        # Filter by category if specified
        if category:
            mock_markets = [m for m in mock_markets if m.category == category]

        return mock_markets[:limit]

    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get specific market by ID for mock client"""
        logger.info(f"MockMarketClient: Fetching market {market_id} for {self.platform}")
        markets = await self.get_markets()
        for market in markets:
            if market.id == market_id:
                return market
        return None

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place mock order"""
        logger.info(f"MockMarketClient: Placing mock order for market {order.market_id}")
        return OrderResponse(
            success=True,
            order_id=f"mock_order_{int(time.time())}",
            filled_quantity=order.quantity,
            average_price=order.price or 0.5,
            total_cost=(order.price or 0.5) * order.quantity,
            fees=0.01 * (order.price or 0.5) * order.quantity,
            error_message=None,
            timestamp=datetime.utcnow()
        )

    async def get_user_balance(self) -> Dict[str, float]:
        """Get mock user balance"""
        logger.info(f"MockMarketClient: Fetching mock balance for {self.platform}")
        return {"USD": 10000.0, "MANA": 5000.0}

    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get mock user orders"""
        logger.info(f"MockMarketClient: Fetching mock orders for {self.platform}, market: {market_id}")
        return []

class PolymarketRealClient(BaseAPIClient):
    """
    Real Polymarket API Client
    
    Polymarket provides a public API for reading market data.
    Authentication is required for trading operations.
    """
    
    def _get_default_headers(self) -> Dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0'
        }
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        return headers
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get markets from Polymarket"""
        logger.info(f"PolymarketClient: Fetching markets (category: {category}, limit: {limit})")
        params = {
            'limit': min(limit, 200),  # Polymarket max limit
            'active': 'true'
        }
        if category:
            params['category'] = category
        
        try:
            response = await self._make_request('GET', '/markets', params=params)
            markets = response.get('markets', [])
            
            transformed_markets = []
            for market in markets:
                transformed_market = MarketData(
                    id=market.get('id'),
                    platform='polymarket',
                    question=market.get('question', ''),
                    description=market.get('description'),
                    category=market.get('category'),
                    market_type=market.get('type', 'BINARY'),
                    outcomes=market.get('outcomes', ['Yes', 'No']),
                    current_price=market.get('price'),
                    probability=market.get('probability'),
                    volume_24h=market.get('volume24Hours', 0),
                    total_volume=market.get('volume', 0),
                    liquidity=market.get('liquidity', 0),
                    open_time=self._parse_datetime(market.get('startDate')),
                    close_time=self._parse_datetime(market.get('endDate')),
                    resolution_date=self._parse_datetime(market.get('resolutionDate')),
                    status='open' if market.get('isActive') else 'closed',
                    url=f"https://polymarket.com/market/{market.get('slug', market.get('id'))}",
                    last_updated=datetime.utcnow()
                )
                transformed_markets.append(transformed_market)
            
            return transformed_markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get specific market details from Polymarket"""
        logger.info(f"PolymarketClient: Fetching market {market_id}")
        try:
            response = await self._make_request('GET', f'/markets/{market_id}')
            market = response.get('market', response)
            
            return MarketData(
                id=market.get('id'),
                platform='polymarket',
                question=market.get('question', ''),
                description=market.get('description'),
                category=market.get('category'),
                market_type=market.get('type', 'BINARY'),
                outcomes=market.get('outcomes', ['Yes', 'No']),
                current_price=market.get('price'),
                probability=market.get('probability'),
                volume_24h=market.get('volume24Hours', 0),
                total_volume=market.get('volume', 0),
                liquidity=market.get('liquidity', 0),
                open_time=self._parse_datetime(market.get('startDate')),
                close_time=self._parse_datetime(market.get('endDate')),
                resolution_date=self._parse_datetime(market.get('resolutionDate')),
                status='open' if market.get('isActive') else 'closed',
                url=f"https://polymarket.com/market/{market.get('slug', market.get('id'))}",
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket market {market_id}: {e}")
            return None
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Polymarket"""
        logger.info(f"PolymarketClient: Placing order for market {order.market_id}")
        try:
            order_data = {
                'market_id': order.market_id,
                'outcome': order.outcome,
                'order_type': order.order_type,
                'quantity': order.quantity,
                'time_in_force': order.time_in_force
            }
            if order.price:
                order_data['price'] = order.price
            
            response = await self._make_request('POST', '/orders', json=order_data)
            
            return OrderResponse(
                success=True,
                order_id=response.get('order_id'),
                filled_quantity=response.get('filled_quantity', 0),
                average_price=response.get('average_price'),
                total_cost=response.get('total_cost'),
                fees=response.get('fees', 0),
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Failed to place order on Polymarket: {e}")
            return OrderResponse(
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
            
    async def get_user_balance(self) -> Dict[str, float]:
        """Get Polymarket user balance"""
        logger.info("PolymarketClient: Fetching user balance")
        try:
            response = await self._make_request('GET', '/account/balance')
            return response.get('balances', {})
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket balance: {e}")
            return {}
    
    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get Polymarket user orders"""
        logger.info(f"PolymarketClient: Fetching user orders for market: {market_id}")
        try:
            params = {}
            if market_id:
                params['market_id'] = market_id
            
            response = await self._make_request('GET', '/account/orders', params=params)
            return response.get('orders', [])
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket orders: {e}")
            return []

class KalshiRealClient(BaseAPIClient):
    """
    Real Kalshi API Client
    
    Kalshi provides API access for market data and trading.
    Requires API key authentication.
    """
    
    def _get_default_headers(self) -> Dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0',
            'X-API-Key': self.config.api_key
        }
        if self.config.secret_key:
            timestamp = str(int(time.time()))
            # Kalshi API expects message to be signed with (timestamp + SECRET_KEY)
            message = timestamp + self.config.secret_key
            signature = hmac.new(
                self.config.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            headers['X-Timestamp'] = timestamp
            headers['X-Signature'] = signature
        return headers
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get Kalshi markets"""
        logger.info(f"KalshiClient: Fetching markets (category: {category}, limit: {limit})")
        params = {'limit': min(limit, 100)}
        if category:
            params['category'] = category
        
        try:
            response = await self._make_request('GET', '/markets', params=params)
            markets = response.get('markets', [])
            
            transformed_markets = []
            for market_data in markets:
                transformed_market = MarketData(
                    id=market_data.get('ticker'),
                    platform='kalshi',
                    question=market_data.get('title', ''),
                    description=market_data.get('subtitle'),
                    category=market_data.get('category'),
                    market_type='binary',
                    outcomes=['Yes', 'No'],
                    current_price=market_data.get('last_price'),
                    probability=market_data.get('last_price'),
                    volume_24h=market_data.get('volume_24h', 0),
                    total_volume=market_data.get('total_volume', 0),
                    liquidity=market_data.get('open_interest', 0),
                    open_time=self._parse_timestamp(market_data.get('open_time')),
                    close_time=self._parse_timestamp(market_data.get('close_time')),
                    resolution_date=self._parse_timestamp(market_data.get('expiration_time')),
                    status='open' if market_data.get('is_open') else 'closed',
                    url=f"https://kalshi.com/trade/{market_data.get('ticker')}",
                    last_updated=datetime.utcnow()
                )
                transformed_markets.append(transformed_market)
            
            return transformed_markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get Kalshi market details"""
        logger.info(f"KalshiClient: Fetching market {market_id}")
        try:
            response = await self._make_request('GET', f'/markets/{market_id}')
            market_data = response.get('market', response)
            
            return MarketData(
                id=market_data.get('ticker'),
                platform='kalshi',
                question=market_data.get('title', ''),
                description=market_data.get('subtitle'),
                category=market_data.get('category'),
                market_type='binary',
                outcomes=['Yes', 'No'],
                current_price=market_data.get('last_price'),
                probability=market_data.get('last_price'),
                volume_24h=market_data.get('volume_24h', 0),
                total_volume=market_data.get('total_volume', 0),
                liquidity=market_data.get('open_interest', 0),
                open_time=self._parse_timestamp(market_data.get('open_time')),
                close_time=self._parse_timestamp(market_data.get('close_time')),
                resolution_date=self._parse_timestamp(market_data.get('expiration_time')),
                status='open' if market_data.get('is_open') else 'closed',
                url=f"https://kalshi.com/trade/{market_data.get('ticker')}",
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi market {market_id}: {e}")
            return None
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Kalshi"""
        logger.info(f"KalshiClient: Placing order for market {order.market_id}")
        try:
            order_data = {
                'ticker': order.market_id,
                'side': 'BUY' if order.order_type == 'buy' else 'SELL',
                'count': order.quantity,
                'type': 'LIMIT', # Assuming limit orders for now
                'expiration_time': int(time.time()) + 3600  # 1 hour from now
            }
            if order.price:
                order_data['price'] = order.price
            
            response = await self._make_request('POST', '/orders', json=order_data)
            
            return OrderResponse(
                success=True,
                order_id=response.get('id'),
                filled_quantity=response.get('filled', 0),
                average_price=response.get('average_price'),
                total_cost=response.get('total_cost'),
                fees=response.get('fees', 0),
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Failed to place order on Kalshi: {e}")
            return OrderResponse(
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_user_balance(self) -> Dict[str, float]:
        """Get Kalshi user balance"""
        logger.info("KalshiClient: Fetching user balance")
        try:
            response = await self._make_request('GET', '/account')
            account_data = response.get('account', {})
            return {
                'USD': account_data.get('buying_power', 0),
                'collateral': account_data.get('collateral', 0)
            }
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi balance: {e}")
            return {}
    
    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get Kalshi user orders"""
        logger.info(f"KalshiClient: Fetching user orders for market: {market_id}")
        try:
            params = {}
            if market_id:
                params['ticker'] = market_id
            
            response = await self._make_request('GET', '/orders', params=params)
            return response.get('orders', [])
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi orders: {e}")
            return []

class ManifoldRealClient(BaseAPIClient):
    """
    Real Manifold Markets API Client
    
    Manifold provides public API access for market data.
    Authentication required for trading operations.
    """
    
    def _get_default_headers(self) -> Dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0'
        }
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        return headers
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get markets from Manifold"""
        logger.info(f"ManifoldClient: Fetching markets (category: {category}, limit: {limit})")
        params = {'limit': min(limit, 200)}
        if category:
            params['category'] = category
        
        try:
            response = await self._make_request('GET', '/markets', params=params)
            markets = response.get('markets', [])
            
            transformed_markets = []
            for market_data in markets:
                transformed_market = MarketData(
                    id=market_data.get('id'),
                    platform='manifold',
                    question=market_data.get('question', ''),
                    description=market_data.get('description'),
                    category=market_data.get('groupSlugs', [None])[0] or "Uncategorized", # Manifold uses groupSlugs
                    market_type=market_data.get('outcomeType', 'BINARY'),
                    outcomes=self._get_outcomes(market_data.get('outcomeType')),
                    current_price=market_data.get('probability'), # Manifold uses probability for binary markets
                    probability=market_data.get('probability'),
                    volume_24h=market_data.get('volume24Hours', 0),
                    total_volume=market_data.get('volume', 0),
                    liquidity=market_data.get('totalLiquidity', 0),
                    open_time=self._parse_datetime(market_data.get('createdTime')),
                    close_time=self._parse_datetime(market_data.get('closeTime')),
                    status='open' if not market_data.get('isResolved') else 'resolved',
                    url=f"https://manifold.markets/{market_data.get('creatorUsername', '')}/{market_data.get('slug', '')}",
                    last_updated=datetime.utcnow()
                )
                transformed_markets.append(transformed_market)
            
            return transformed_markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Manifold markets: {e}")
            return []
    
    def _get_outcomes(self, outcome_type: str) -> List[str]:
        """Helper to get outcomes based on market type"""
        if outcome_type == 'BINARY':
            return ['Yes', 'No']
        elif outcome_type == 'FREE_RESPONSE': # Not directly supported in MarketData
            return ['Free Response']
        elif outcome_type == 'MULTIPLE_CHOICE': # Not directly supported in MarketData
            return ['Multiple Choice']
        return ['Yes', 'No'] # Default for unknown types
    
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get Manifold market details"""
        logger.info(f"ManifoldClient: Fetching market {market_id}")
        try:
            response = await self._make_request('GET', f'/market/{market_id}')
            market_data = response
            
            return MarketData(
                id=market_data.get('id'),
                platform='manifold',
                question=market_data.get('question', ''),
                description=market_data.get('text'), # Manifold uses 'text' for description
                category=market_data.get('groupSlugs', [None])[0] or "Uncategorized",
                market_type=market_data.get('outcomeType', 'BINARY'),
                outcomes=self._get_outcomes(market_data.get('outcomeType')),
                current_price=market_data.get('probability'),
                probability=market_data.get('probability'),
                volume_24h=market_data.get('volume24Hours', 0),
                total_volume=market_data.get('volume', 0),
                liquidity=market_data.get('totalLiquidity', 0),
                open_time=self._parse_datetime(market_data.get('createdTime')),
                close_time=self._parse_datetime(market_data.get('closeTime')),
                status='open' if not market_data.get('isResolved') else 'resolved',
                url=f"https://manifold.markets/{market_data.get('creatorUsername', '')}/{market_data.get('slug', '')}",
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Manifold market {market_id}: {e}")
            return None
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Manifold"""
        logger.info(f"ManifoldClient: Placing order for market {order.market_id}")
        try:
            # Manifold has a simpler bet structure
            order_data = {
                'contractId': order.market_id, # Manifold uses contractId
                'amount': order.quantity,
                'outcome': order.outcome,
                'limitProb': order.price # Manifold uses limitProb
            }
            if order.order_type == 'sell':
                # Manifold sell is against an existing position, more complex
                raise NotImplementedError("Selling is more complex on Manifold and not yet implemented.")

            response = await self._make_request('POST', '/bet', json=order_data)
            
            return OrderResponse(
                success=True,
                order_id=response.get('id'),
                filled_quantity=response.get('amount', 0), # Manifold returns amount bet
                average_price=response.get('limitProb'),
                total_cost=response.get('amount'),
                fees=response.get('fees', 0),
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Failed to place order on Manifold: {e}")
            return OrderResponse(
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_user_balance(self) -> Dict[str, float]:
        """Get Manifold user balance"""
        logger.info("ManifoldClient: Fetching user balance")
        try:
            response = await self._make_request('GET', '/me') # Assumes pre-authenticated user
            user_data = response
            return {
                'MANA': user_data.get('balance', 0) # Manifold uses MANA currency
            }
        except Exception as e:
            logger.error(f"Failed to fetch Manifold balance: {e}")
            return {}
    
    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get Manifold user orders"""
        logger.info(f"ManifoldClient: Fetching user orders for market: {market_id}")
        try:
            params = {}
            if market_id:
                params['contractId'] = market_id
            
            response = await self._make_request('GET', '/bets', params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to fetch Manifold orders: {e}")
            return []

class NewsAPIClient(BaseAPIClient):
    """
    News API Client for market sentiment analysis
    
    Integrates with NewsAPI, Alpha Vantage news, and other news sources
    to provide sentiment analysis for prediction markets.
    """
    
    def _get_default_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0',
            'X-Api-Key': self.config.api_key # NewsAPI uses X-Api-Key header
        }
    
    async def get_market_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """Get news articles related to a market query"""
        logger.info(f"NewsAPIClient: Fetching news for query: {query}, days_back: {days_back}")
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 50
            }
            
            response = await self._make_request('GET', '/everything', params=params)
            articles = response.get('articles', [])
            
            transformed_articles = []
            for article in articles:
                transformed_article = {
                    'title': article.get('title', ''),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'published_at': self._parse_datetime(article.get('publishedAt')),
                    'source': article.get('source', {}).get('name'),
                    'author': article.get('author'),
                    'content': article.get('content'),
                    'url_to_image': article.get('urlToImage')
                }
                transformed_articles.append(transformed_article)
            
            return transformed_articles
                
        except Exception as e:
            logger.error(f"Failed to fetch news for query {query}: {e}")
            return []
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Not applicable for NewsAPI client"""
        return []

    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Not applicable for NewsAPI client"""
        return None

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Not applicable for NewsAPI client"""
        return OrderResponse(success=False, error_message="Not applicable for NewsAPI client")

    async def get_user_balance(self) -> Dict[str, float]:
        """Not applicable for NewsAPI client"""
        return {}

    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Not applicable for NewsAPI client"""
        return []

class PredictionMarketAggregator:
    """Aggregates data from multiple prediction market platforms"""
    
    def __init__(self, api_configs: Dict[str, APIConfig]):
        self.api_configs = api_configs
        self.clients: Dict[str, Union[BaseAPIClient, MockMarketClient]] = {}
        # Cache for market data
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 60 # seconds for market list cache
        
    async def initialize_clients(self):
        """Initialize all API clients (real or mock) based on configurations"""
        for platform, config in self.api_configs.items():
            if platform == "news": # News is handled separately
                if config.api_key:
                    self.clients[platform] = NewsAPIClient(config)
                    logger.info(f"Initialized real NewsAPIClient.")
                else:
                    logger.warning(f"NewsAPI key not configured. News features will be unavailable.")
                continue

            if config.api_key:
                try:
                    if platform == 'polymarket':
                        self.clients[platform] = PolymarketRealClient(config)
                    elif platform == 'kalshi':
                        self.clients[platform] = KalshiRealClient(config)
                    elif platform == 'manifold':
                        self.clients[platform] = ManifoldRealClient(config)
                    else:
                        logger.warning(f"Unknown real platform client: {platform}. Using mock client.")
                        self.clients[platform] = MockMarketClient(platform)
                    logger.info(f"Initialized real client for {platform}.")
                except Exception as e:
                    logger.error(f"Failed to initialize real client for {platform}: {e}. Falling back to mock client.")
                    self.clients[platform] = MockMarketClient(platform)
            else:
                logger.warning(f"API key not configured for {platform}. Using mock client.")
                self.clients[platform] = MockMarketClient(platform)
                
    async def get_all_markets(self, category: Optional[str] = None, limit_per_platform: int = 50) -> List[MarketData]:
        """Get markets from all configured platforms"""
        all_markets: List[MarketData] = []
        
        tasks_to_run = []
        platforms_in_tasks = []

        for platform, client in self.clients.items():
            if isinstance(client, (PolymarketRealClient, KalshiRealClient, ManifoldRealClient, MockMarketClient)):
                tasks_to_run.append(client.get_markets(category, limit_per_platform))
                platforms_in_tasks.append(platform)
        
        results = await asyncio.gather(*tasks_to_run, return_exceptions=True)
        
        for platform, result in zip(platforms_in_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch markets from {platform}: {result}")
                continue
            
            markets = result
            for market in markets:
                market.platform = platform # Ensure platform is correctly set
            all_markets.extend(markets)
        
        # Sort by volume (descending)
        all_markets.sort(key=lambda x: x.volume_24h, reverse=True)
        
        return all_markets
    
    async def get_market_details(self, market_id: str) -> Optional[MarketData]:
        """Get detailed information for a specific market from its platform"""
        for platform, client in self.clients.items():
            if isinstance(client, (PolymarketRealClient, KalshiRealClient, ManifoldRealClient, MockMarketClient)):
                try:
                    market = await client.get_market(market_id)
                    if market and market.id == market_id: # Confirm the market returned is the one requested
                        return market
                except Exception as e:
                    logger.error(f"Error fetching market {market_id} from {platform}: {e}")
        return None

    async def compare_market(self, question: str) -> Dict[str, Optional[MarketData]]:
        """Compare the same market across platforms using question similarity"""
        results: Dict[str, Optional[MarketData]] = {}
        
        tasks_to_run = []
        platforms_in_tasks = []

        for platform, client in self.clients.items():
            if isinstance(client, (PolymarketRealClient, KalshiRealClient, ManifoldRealClient, MockMarketClient)):
                tasks_to_run.append(client.get_markets(limit=100)) # Fetch more markets for comparison
                platforms_in_tasks.append(platform) # Keep track of platforms
            
        all_platform_markets = await asyncio.gather(*tasks_to_run, return_exceptions=True)

        for platform, markets_result in zip(platforms_in_tasks, all_platform_markets):
            if isinstance(markets_result, Exception):
                logger.error(f"Error fetching markets to compare from {platform}: {markets_result}")
                results[platform] = None
                continue
            
            best_match: Optional[MarketData] = None
            highest_similarity = 0.0

            for market in markets_result:
                similarity = self._questions_similar(question, market.question)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = market
            
            if best_match and highest_similarity >= 0.7: # Threshold for considering a match
                results[platform] = best_match
            else:
                results[platform] = None
        
        return results
    
    @staticmethod
    def _questions_similar(question1: str, question2: str, threshold: float = 0.7) -> float:
        """Calculate similarity between two questions (Jaccard index)"""
        words1 = set(question1.lower().split())
        words2 = set(question2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    async def get_news_for_query(self, query: str, days_back: int = 7) -> List[Dict]:
        """Fetch news articles for a given query"""
        news_client = self.clients.get("news")
        if isinstance(news_client, NewsAPIClient):
            return await news_client.get_market_news(query, days_back)
        return []

    async def cleanup(self):
        """Cleanup all clients"""
        for client in self.clients.values():
            if isinstance(client, (PolymarketRealClient, KalshiRealClient, ManifoldRealClient, NewsAPIClient, MockMarketClient)):
                await client.__aexit__(None, None, None) # Explicitly call aexit for real clients
        logger.info("Prediction market aggregator cleaned up")

# Example usage and testing functions (now integrated into the aggregator logic)
async def test_aggregator():
    """Test the PredictionMarketAggregator with sample configs"""
    # Dummy API configs for testing (replace with actual .env loaded configs)
    configs = {
        "polymarket": APIConfig(api_key="POLYMARKET_TEST_KEY", base_url="https://gamma-api.polymarket.com"),
        "kalshi": APIConfig(api_key="KALSHI_TEST_KEY", secret_key="KALSHI_TEST_SECRET", base_url="https://trading-api.kalshi.com/v2"),
        "manifold": APIConfig(api_key="MANIFOLD_TEST_KEY", base_url="https://api.manifold.markets/v0"),
        "news": APIConfig(api_key="NEWS_TEST_KEY", base_url="https://newsapi.org/v2")
    }

    aggregator = PredictionMarketAggregator(configs)
    await aggregator.initialize_clients() # This will use mock clients if API keys are empty

    print("Testing market fetching...")
    markets = await aggregator.get_all_markets(limit_per_platform=5)
    print(f"Fetched {len(markets)} markets.")
    for market in markets:
        print(f"- {market.question} ({market.platform}): {market.current_price}")

    print("\nTesting market comparison...")
    comparison_results = await aggregator.compare_market("Will Bitcoin reach $100,000?")
    for platform, market in comparison_results.items():
        if market:
            print(f"- {platform}: {market.question} ({market.current_price})")
        else:
            print(f"- {platform}: No similar market found.")
            
    # Test news fetching
    print("\nTesting news fetching...")
    news_articles = await aggregator.get_news_for_query("AI development")
    print(f"Fetched {len(news_articles)} news articles.")
    if news_articles:
        print(f"- Sample news: {news_articles[0].get('title')} from {news_articles[0].get('source')}")

    await aggregator.cleanup()
    print("Aggregator testing complete.")

if __name__ == "__main__":
    asyncio.run(test_aggregator())