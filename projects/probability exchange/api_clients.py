#!/usr/bin/env python3
"""
API Integration Clients for MarketPulse Pro Betting Platform

This module provides unified API clients for Polymarket, Kalshi, and Manifold
with consistent interfaces, error handling, and rate limiting.
"""

import asyncio
import aiohttp
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from urllib.parse import urljoin, urlencode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIRateLimit:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    burst_limit: int = 10
    current_requests: int = 0
    window_start: float = 0.0

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
        self.tokens = burst_limit
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire a token for making a request"""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_refill
            tokens_to_add = int(time_passed * self.requests_per_minute / 60)
            
            if tokens_to_add > 0:
                self.tokens = min(self.burst_limit, self.tokens + tokens_to_add)
                self.last_refill = now
            
            if self.tokens > 0:
                self.tokens -= 1
                return True
            
            return False
    
    async def wait_for_token(self):
        """Wait until a token is available"""
        while not await self.acquire():
            await asyncio.sleep(1 / self.requests_per_minute)

class BaseAPIClient(ABC):
    """Base class for all prediction market API clients"""
    
    def __init__(self, api_key: str, base_url: str, rate_limit: int = 60):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limit)
        self.session = None
        self.last_request_time = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
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
        """Make a rate-limited API request"""
        await self.rate_limiter.wait_for_token()
        
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.get('headers', {})
        headers.update(self._get_default_headers())
        kwargs['headers'] = headers
        
        # Add authentication
        if self.api_key:
            kwargs = self._add_authentication(kwargs)
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    raise aiohttp.ClientError(f"API Error {response.status}: {response_data}")
                
                return response_data
                
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    @abstractmethod
    def _add_authentication(self, kwargs: Dict) -> Dict:
        """Add authentication to request kwargs"""
        pass

class PolymarketClient(BaseAPIClient):
    """Polymarket API client"""
    
    def _get_default_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0'
        }
    
    def _add_authentication(self, kwargs: Dict) -> Dict:
        if 'params' not in kwargs:
            kwargs['params'] = {}
        kwargs['params']['api_key'] = self.api_key
        return kwargs
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get Polymarket markets"""
        params = {'limit': limit}
        if category:
            params['category'] = category
        
        try:
            response = await self._make_request('GET', '/markets', params=params)
            markets = []
            
            for market_data in response.get('markets', []):
                market = MarketData(
                    id=market_data.get('id'),
                    platform='polymarket',
                    question=market_data.get('question', ''),
                    description=market_data.get('description'),
                    category=market_data.get('category'),
                    market_type=market_data.get('type', 'binary'),
                    outcomes=market_data.get('outcomes', ['Yes', 'No']),
                    current_price=market_data.get('price'),
                    probability=market_data.get('probability'),
                    volume_24h=market_data.get('volume_24h', 0),
                    total_volume=market_data.get('volume', 0),
                    liquidity=market_data.get('liquidity', 0),
                    open_time=datetime.fromisoformat(market_data.get('open_time', '').replace('Z', '+00:00')) if market_data.get('open_time') else None,
                    close_time=datetime.fromisoformat(market_data.get('close_time', '').replace('Z', '+00:00')) if market_data.get('close_time') else None,
                    status=market_data.get('status', 'open'),
                    url=market_data.get('url'),
                    last_updated=datetime.utcnow()
                )
                markets.append(market)
            
            return markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get Polymarket market details"""
        try:
            response = await self._make_request('GET', f'/markets/{market_id}')
            market_data = response.get('market', {})
            
            return MarketData(
                id=market_data.get('id'),
                platform='polymarket',
                question=market_data.get('question', ''),
                description=market_data.get('description'),
                category=market_data.get('category'),
                market_type=market_data.get('type', 'binary'),
                outcomes=market_data.get('outcomes', ['Yes', 'No']),
                current_price=market_data.get('price'),
                probability=market_data.get('probability'),
                volume_24h=market_data.get('volume_24h', 0),
                total_volume=market_data.get('volume', 0),
                liquidity=market_data.get('liquidity', 0),
                open_time=datetime.fromisoformat(market_data.get('open_time', '').replace('Z', '+00:00')) if market_data.get('open_time') else None,
                close_time=datetime.fromisoformat(market_data.get('close_time', '').replace('Z', '+00:00')) if market_data.get('close_time') else None,
                status=market_data.get('status', 'open'),
                url=market_data.get('url'),
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket market {market_id}: {e}")
            return None
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Polymarket"""
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
            return OrderResponse(
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_user_balance(self) -> Dict[str, float]:
        """Get Polymarket user balance"""
        try:
            response = await self._make_request('GET', '/account/balance')
            return response.get('balances', {})
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket balance: {e}")
            return {}
    
    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get Polymarket user orders"""
        try:
            params = {}
            if market_id:
                params['market_id'] = market_id
            
            response = await self._make_request('GET', '/account/orders', params=params)
            return response.get('orders', [])
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket orders: {e}")
            return []

class KalshiClient(BaseAPIClient):
    """Kalshi API client"""
    
    def _get_default_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0',
            'X-API-Key': self.api_key
        }
    
    def _add_authentication(self, kwargs: Dict) -> Dict:
        # Authentication is handled in headers for Kalshi
        return kwargs
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get Kalshi markets"""
        params = {'limit': limit}
        if category:
            params['category'] = category
        
        try:
            response = await self._make_request('GET', '/markets', params=params)
            markets = []
            
            for market_data in response.get('markets', []):
                market = MarketData(
                    id=market_data.get('ticker'),
                    platform='kalshi',
                    question=market_data.get('title', ''),
                    description=market_data.get('subtitle'),
                    category=market_data.get('category'),
                    market_type='binary',  # Kalshi primarily does binary markets
                    outcomes=['Yes', 'No'],
                    current_price=market_data.get('last_price'),
                    probability=market_data.get('last_price'),
                    volume_24h=market_data.get('volume_24h', 0),
                    total_volume=market_data.get('total_volume', 0),
                    liquidity=market_data.get('open_interest', 0),
                    open_time=datetime.fromtimestamp(market_data.get('open_time', 0)) if market_data.get('open_time') else None,
                    close_time=datetime.fromtimestamp(market_data.get('close_time', 0)) if market_data.get('close_time') else None,
                    resolution_date=datetime.fromtimestamp(market_data.get('expiration_time', 0)) if market_data.get('expiration_time') else None,
                    status='open' if market_data.get('is_open') else 'closed',
                    last_updated=datetime.utcnow()
                )
                markets.append(market)
            
            return markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get Kalshi market details"""
        try:
            response = await self._make_request('GET', f'/markets/{market_id}')
            market_data = response.get('market', {})
            
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
                open_time=datetime.fromtimestamp(market_data.get('open_time', 0)) if market_data.get('open_time') else None,
                close_time=datetime.fromtimestamp(market_data.get('close_time', 0)) if market_data.get('close_time') else None,
                resolution_date=datetime.fromtimestamp(market_data.get('expiration_time', 0)) if market_data.get('expiration_time') else None,
                status='open' if market_data.get('is_open') else 'closed',
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi market {market_id}: {e}")
            return None
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Kalshi"""
        try:
            order_data = {
                'ticker': order.market_id,
                'side': 'BUY' if order.order_type == 'buy' else 'SELL',
                'count': order.quantity,
                'type': 'LIMIT',
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
            return OrderResponse(
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_user_balance(self) -> Dict[str, float]:
        """Get Kalshi user balance"""
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
        try:
            params = {}
            if market_id:
                params['ticker'] = market_id
            
            response = await self._make_request('GET', '/orders', params=params)
            return response.get('orders', [])
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi orders: {e}")
            return []

class ManifoldClient(BaseAPIClient):
    """Manifold Markets API client"""
    
    def _get_default_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0'
        }
    
    def _add_authentication(self, kwargs: Dict) -> Dict:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = f'Bearer {self.api_key}'
        return kwargs
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[MarketData]:
        """Get Manifold markets"""
        params = {'limit': limit}
        if category:
            params['category'] = category
        
        try:
            response = await self._make_request('GET', '/markets', params=params)
            markets = []
            
            for market_data in response.get('markets', []):
                market = MarketData(
                    id=market_data.get('id'),
                    platform='manifold',
                    question=market_data.get('question', ''),
                    description=market_data.get('description'),
                    category=market_data.get('category'),
                    market_type=market_data.get('outcomeType', 'BINARY'),
                    outcomes=self._get_outcomes_from_type(market_data.get('outcomeType')),
                    current_price=market_data.get('probability'),
                    probability=market_data.get('probability'),
                    volume_24h=market_data.get('volume24Hours', 0),
                    total_volume=market_data.get('volume', 0),
                    liquidity=market_data.get('liquidity', 0),
                    open_time=datetime.fromisoformat(market_data.get('createdTime', '').replace('Z', '+00:00')) if market_data.get('createdTime') else None,
                    close_time=datetime.fromisoformat(market_data.get('closeTime', '').replace('Z', '+00:00')) if market_data.get('closeTime') else None,
                    status='open' if market_data.get('isResolved') is False else 'resolved',
                    url=f"https://manifold.markets/{market_data.get('creatorUsername', '')}/{market_data.get('slug', '')}",
                    last_updated=datetime.utcnow()
                )
                markets.append(market)
            
            return markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Manifold markets: {e}")
            return []
    
    def _get_outcomes_from_type(self, outcome_type: str) -> List[str]:
        """Get outcomes based on market type"""
        if outcome_type == 'BINARY':
            return ['Yes', 'No']
        elif outcome_type == 'FREE_RESPONSE':
            return ['Any answer']
        elif outcome_type == 'MULTIPLE_CHOICE':
            return ['Option A', 'Option B', 'Option C']  # Would need to fetch actual options
        else:
            return ['Yes', 'No']
    
    async def get_market(self, market_id: str) -> Optional[MarketData]:
        """Get Manifold market details"""
        try:
            response = await self._make_request('GET', f'/market/{market_id}')
            market_data = response.get('market', {})
            
            return MarketData(
                id=market_data.get('id'),
                platform='manifold',
                question=market_data.get('question', ''),
                description=market_data.get('description'),
                category=market_data.get('category'),
                market_type=market_data.get('outcomeType', 'BINARY'),
                outcomes=self._get_outcomes_from_type(market_data.get('outcomeType')),
                current_price=market_data.get('probability'),
                probability=market_data.get('probability'),
                volume_24h=market_data.get('volume24Hours', 0),
                total_volume=market_data.get('volume', 0),
                liquidity=market_data.get('liquidity', 0),
                open_time=datetime.fromisoformat(market_data.get('createdTime', '').replace('Z', '+00:00')) if market_data.get('createdTime') else None,
                close_time=datetime.fromisoformat(market_data.get('closeTime', '').replace('Z', '+00:00')) if market_data.get('closeTime') else None,
                status='open' if market_data.get('isResolved') is False else 'resolved',
                url=f"https://manifold.markets/{market_data.get('creatorUsername', '')}/{market_data.get('slug', '')}",
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Manifold market {market_id}: {e}")
            return None
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order on Manifold"""
        try:
            order_data = {
                'marketId': order.market_id,
                'outcome': order.outcome,
                'amount': order.quantity,
                'type': 'BUY' if order.order_type == 'buy' else 'SELL'
            }
            
            if order.price:
                order_data['limitPrice'] = order.price
            
            response = await self._make_request('POST', '/bet', json=order_data)
            
            return OrderResponse(
                success=True,
                order_id=response.get('id'),
                filled_quantity=response.get('shares', 0),
                average_price=response.get('limitPrice'),
                total_cost=response.get('amount'),
                fees=response.get('fees', 0),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return OrderResponse(
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_user_balance(self) -> Dict[str, float]:
        """Get Manifold user balance"""
        try:
            response = await self._make_request('GET', '/me')
            user_data = response.get('user', {})
            return {
                'MONEY': user_data.get('balance', 0)
            }
        except Exception as e:
            logger.error(f"Failed to fetch Manifold balance: {e}")
            return {}
    
    async def get_user_orders(self, market_id: Optional[str] = None) -> List[Dict]:
        """Get Manifold user orders"""
        try:
            params = {}
            if market_id:
                params['marketId'] = market_id
            
            response = await self._make_request('GET', '/bets', params=params)
            return response.get('bets', [])
        except Exception as e:
            logger.error(f"Failed to fetch Manifold orders: {e}")
            return []

class PredictionMarketAggregator:
    """Aggregates data from multiple prediction market platforms"""
    
    def __init__(self):
        self.clients = {}
        
    def add_client(self, platform: str, client: BaseAPIClient):
        """Add an API client for a platform"""
        self.clients[platform] = client
    
    async def get_all_markets(self, category: Optional[str] = None, limit_per_platform: int = 50) -> List[MarketData]:
        """Get markets from all configured platforms"""
        all_markets = []
        
        # Run API calls concurrently
        tasks = []
        for platform, client in self.clients.items():
            task = self._get_markets_safe(client, category, limit_per_platform)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (platform, result) in enumerate(zip(self.clients.keys(), results)):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch markets from {platform}: {result}")
                continue
            
            markets = result
            for market in markets:
                market.platform = platform  # Ensure platform is set
            
            all_markets.extend(markets)
        
        # Sort by volume (descending)
        all_markets.sort(key=lambda x: x.volume_24h, reverse=True)
        
        return all_markets
    
    async def _get_markets_safe(self, client: BaseAPIClient, category: Optional[str], limit: int) -> List[MarketData]:
        """Safely get markets from a client with error handling"""
        try:
            return await client.get_markets(category, limit)
        except Exception as e:
            logger.error(f"Error getting markets: {e}")
            return []
    
    async def compare_market(self, question: str) -> Dict[str, Optional[MarketData]]:
        """Compare the same market across platforms"""
        results = {}
        
        for platform, client in self.clients.items():
            try:
                # Search for markets with similar questions
                markets = await client.get_markets(limit=100)
                matching_markets = [
                    m for m in markets 
                    if self._questions_similar(question, m.question)
                ]
                
                if matching_markets:
                    results[platform] = matching_markets[0]  # Take the best match
                else:
                    results[platform] = None
                    
            except Exception as e:
                logger.error(f"Error comparing market on {platform}: {e}")
                results[platform] = None
        
        return results
    
    def _questions_similar(self, question1: str, question2: str, threshold: float = 0.7) -> bool:
        """Simple similarity check between questions"""
        words1 = set(question1.lower().split())
        words2 = set(question2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold

# Example usage and testing functions
async def test_api_clients():
    """Test API clients with sample data"""
    # This would require real API keys to test
    print("Testing Prediction Market API Clients...")
    
    # Example usage
    aggregator = PredictionMarketAggregator()
    
    # Add clients (would need real API keys)
    # polymarket_client = PolymarketClient(api_key="your_key", base_url="https://gamma-api.polymarket.com")
    # kalshi_client = KalshiClient(api_key="your_key", base_url="https://trading-api.kalshi.com/v2")
    # manifold_client = ManifoldClient(api_key="your_key", base_url="https://api.manifold.markets/v0")
    
    # aggregator.add_client("polymarket", polymarket_client)
    # aggregator.add_client("kalshi", kalshi_client)
    # aggregator.add_client("manifold", manifold_client)
    
    # async with aggregator.clients["polymarket"] as client:
    #     markets = await client.get_markets(category="politics", limit=10)
    #     print(f"Found {len(markets)} politics markets on Polymarket")
    
    print("API client framework ready for integration!")

if __name__ == "__main__":
    asyncio.run(test_api_clients())