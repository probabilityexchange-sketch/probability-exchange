#!/usr/bin/env python3
"""
Real API Clients for MarketPulse Pro Prediction Markets

This module implements actual API integrations for:
- Polymarket API
- Kalshi API
- News APIs (NewsAPI, Alpha Vantage, etc.)
- Additional prediction market platforms

Each client handles authentication, rate limiting, error handling,
and data transformation for consistent market data.
"""

import asyncio
import aiohttp
import time
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urljoin
import hashlib
import hmac
import base64

# Import PolyRouter client
from polyrouter_client import PolyRouterClient, create_polyrouter_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API clients"""
    api_key: str
    secret_key: Optional[str] = None
    base_url: str = ""
    rate_limit: int = 60
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class PolymarketRealClient:
    """
    Real Polymarket API Client
    
    Polymarket provides a public API for reading market data.
    Authentication is required for trading operations.
    """
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.base_url = config.base_url or "https://gamma-api.polymarket.com"
        self.session = None
        self.rate_limit_bucket = asyncio.Semaphore(config.rate_limit // 60)  # Requests per minute
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self._get_headers()
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for Polymarket API"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0'
        }
        
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
            
        return headers
    
    async def _rate_limited_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make a rate-limited API request with retry logic"""
        async with self.rate_limit_bucket:
            for attempt in range(self.config.retry_attempts):
                try:
                    url = urljoin(self.base_url, endpoint)
                    
                    async with self.session.request(method, url, **kwargs) as response:
                        if response.status == 429:  # Rate limit exceeded
                            retry_after = int(response.headers.get('Retry-After', 60))
                            logger.warning(f"Rate limit exceeded, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        if response.status >= 400:
                            error_text = await response.text()
                            raise aiohttp.ClientError(f"API Error {response.status}: {error_text}")
                        
                        return await response.json()
                        
                except Exception as e:
                    if attempt == self.config.retry_attempts - 1:
                        raise
                    
                    logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get markets from Polymarket"""
        try:
            params = {
                'limit': min(limit, 200),  # Polymarket max limit
                'active': 'true'
            }
            
            if category:
                params['category'] = category
            
            # Polymarket markets endpoint
            response = await self._rate_limited_request('GET', '/markets', params=params)
            
            markets = response.get('markets', [])
            
            # Transform to consistent format
            transformed_markets = []
            for market in markets:
                try:
                    transformed_market = {
                        'id': market.get('id'),
                        'platform': 'polymarket',
                        'question': market.get('question', ''),
                        'description': market.get('description'),
                        'category': market.get('category'),
                        'market_type': market.get('type', 'BINARY'),
                        'outcomes': market.get('outcomes', ['Yes', 'No']),
                        'current_price': market.get('price'),
                        'probability': market.get('probability'),
                        'volume_24h': market.get('volume24Hours', 0),
                        'total_volume': market.get('volume', 0),
                        'liquidity': market.get('liquidity', 0),
                        'open_time': self._parse_datetime(market.get('startDate')),
                        'close_time': self._parse_datetime(market.get('endDate')),
                        'resolution_date': self._parse_datetime(market.get('resolutionDate')),
                        'status': 'open' if market.get('isActive') else 'closed',
                        'url': f"https://polymarket.com/market/{market.get('slug', market.get('id'))}",
                        'last_updated': datetime.utcnow()
                    }
                    transformed_markets.append(transformed_market)
                except Exception as e:
                    logger.error(f"Error transforming Polymarket market: {e}")
                    continue
            
            logger.info(f"Retrieved {len(transformed_markets)} markets from Polymarket")
            return transformed_markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[Dict]:
        """Get specific market details from Polymarket"""
        try:
            response = await self._rate_limited_request('GET', f'/markets/{market_id}')
            market = response.get('market', response)
            
            return {
                'id': market.get('id'),
                'platform': 'polymarket',
                'question': market.get('question', ''),
                'description': market.get('description'),
                'category': market.get('category'),
                'market_type': market.get('type', 'BINARY'),
                'outcomes': market.get('outcomes', ['Yes', 'No']),
                'current_price': market.get('price'),
                'probability': market.get('probability'),
                'volume_24h': market.get('volume24Hours', 0),
                'total_volume': market.get('volume', 0),
                'liquidity': market.get('liquidity', 0),
                'open_time': self._parse_datetime(market.get('startDate')),
                'close_time': self._parse_datetime(market.get('endDate')),
                'resolution_date': self._parse_datetime(market.get('resolutionDate')),
                'status': 'open' if market.get('isActive') else 'closed',
                'url': f"https://polymarket.com/market/{market.get('slug', market.get('id'))}",
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch Polymarket market {market_id}: {e}")
            return None
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response"""
        if not date_str:
            return None
        
        try:
            # Polymarket uses ISO 8601 format
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse date {date_str}: {e}")
            return None

class KalshiRealClient:
    """
    Real Kalshi API Client
    
    Kalshi provides API access for market data and trading.
    Requires API key authentication.
    """
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.base_url = config.base_url or "https://trading-api.kalshi.com/v2"
        self.session = None
        self.rate_limit_bucket = asyncio.Semaphore(config.rate_limit // 60)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self._get_headers()
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for Kalshi API"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0',
            'X-API-Key': self.config.api_key
        }
        
        if self.config.secret_key:
            # Add signature for authenticated requests
            timestamp = str(int(time.time()))
            message = timestamp + self.config.secret_key
            signature = hmac.new(
                self.config.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Timestamp'] = timestamp
            headers['X-Signature'] = signature
        
        return headers
    
    async def _rate_limited_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make a rate-limited API request with retry logic"""
        async with self.rate_limit_bucket:
            for attempt in range(self.config.retry_attempts):
                try:
                    url = urljoin(self.base_url, endpoint)
                    
                    async with self.session.request(method, url, **kwargs) as response:
                        if response.status == 429:
                            retry_after = int(response.headers.get('Retry-After', 60))
                            logger.warning(f"Kalshi rate limit exceeded, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        if response.status >= 400:
                            error_text = await response.text()
                            raise aiohttp.ClientError(f"Kalshi API Error {response.status}: {error_text}")
                        
                        return await response.json()
                        
                except Exception as e:
                    if attempt == self.config.retry_attempts - 1:
                        raise
                    
                    logger.warning(f"Kalshi request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get markets from Kalshi"""
        try:
            params = {
                'limit': min(limit, 100)
            }
            
            if category:
                params['category'] = category
            
            response = await self._rate_limited_request('GET', '/markets', params=params)
            
            markets = response.get('markets', [])
            
            # Transform to consistent format
            transformed_markets = []
            for market in markets:
                try:
                    transformed_market = {
                        'id': market.get('ticker'),
                        'platform': 'kalshi',
                        'question': market.get('title', ''),
                        'description': market.get('subtitle'),
                        'category': market.get('category'),
                        'market_type': 'BINARY',  # Kalshi primarily binary
                        'outcomes': ['Yes', 'No'],
                        'current_price': market.get('last_price'),
                        'probability': market.get('last_price'),
                        'volume_24h': market.get('volume_24h', 0),
                        'total_volume': market.get('total_volume', 0),
                        'liquidity': market.get('open_interest', 0),
                        'open_time': self._parse_timestamp(market.get('open_time')),
                        'close_time': self._parse_timestamp(market.get('close_time')),
                        'resolution_date': self._parse_timestamp(market.get('expiration_time')),
                        'status': 'open' if market.get('is_open') else 'closed',
                        'url': f"https://kalshi.com/trade/{market.get('ticker')}",
                        'last_updated': datetime.utcnow()
                    }
                    transformed_markets.append(transformed_market)
                except Exception as e:
                    logger.error(f"Error transforming Kalshi market: {e}")
                    continue
            
            logger.info(f"Retrieved {len(transformed_markets)} markets from Kalshi")
            return transformed_markets
            
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[Dict]:
        """Get specific market details from Kalshi"""
        try:
            response = await self._rate_limited_request('GET', f'/markets/{market_id}')
            market = response.get('market', response)
            
            return {
                'id': market.get('ticker'),
                'platform': 'kalshi',
                'question': market.get('title', ''),
                'description': market.get('subtitle'),
                'category': market.get('category'),
                'market_type': 'BINARY',
                'outcomes': ['Yes', 'No'],
                'current_price': market.get('last_price'),
                'probability': market.get('last_price'),
                'volume_24h': market.get('volume_24h', 0),
                'total_volume': market.get('total_volume', 0),
                'liquidity': market.get('open_interest', 0),
                'open_time': self._parse_timestamp(market.get('open_time')),
                'close_time': self._parse_timestamp(market.get('close_time')),
                'resolution_date': self._parse_timestamp(market.get('expiration_time')),
                'status': 'open' if market.get('is_open') else 'closed',
                'url': f"https://kalshi.com/trade/{market.get('ticker')}",
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch Kalshi market {market_id}: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: Optional[float]) -> Optional[datetime]:
        """Parse timestamp from API response"""
        if not timestamp:
            return None
        
        try:
            return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.warning(f"Failed to parse timestamp {timestamp}: {e}")
            return None

class NewsAPIClient:
    """
    News API Client for market sentiment analysis
    
    Integrates with NewsAPI, Alpha Vantage news, and other news sources
    to provide sentiment analysis for prediction markets.
    """
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.base_url = config.base_url or "https://newsapi.org/v2"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={'X-API-Key': self.config.api_key}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_market_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """Get news articles related to a market query"""
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 50
            }
            
            async with self.session.get(f'{self.base_url}/everything', params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    # Transform articles to consistent format
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
                    
                    logger.info(f"Retrieved {len(transformed_articles)} news articles for query: {query}")
                    return transformed_articles
                else:
                    logger.error(f"News API request failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to fetch news for query {query}: {e}")
            return []
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from news API"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Failed to parse news date {date_str}: {e}")
            return None

class ManifoldRealClient:
    """
    Real Manifold Markets API Client
    
    Manifold provides public API access for market data.
    Authentication required for trading operations.
    """
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.base_url = config.base_url or "https://api.manifold.markets/v0"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self._get_headers()
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for Manifold API"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0'
        }
        
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        return headers
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get markets from Manifold"""
        try:
            params = {'limit': min(limit, 200)}
            
            if category:
                params['category'] = category
            
            async with self.session.get(f'{self.base_url}/markets', params=params) as response:
                if response.status == 200:
                    markets = await response.json()
                    
                    # Transform to consistent format
                    transformed_markets = []
                    for market in markets:
                        try:
                            transformed_market = {
                                'id': market.get('id'),
                                'platform': 'manifold',
                                'question': market.get('question', ''),
                                'description': market.get('description'),
                                'category': market.get('category'),
                                'market_type': market.get('outcomeType', 'BINARY'),
                                'outcomes': self._get_outcomes(market.get('outcomeType')),
                                'current_price': market.get('probability'),
                                'probability': market.get('probability'),
                                'volume_24h': market.get('volume24Hours', 0),
                                'total_volume': market.get('volume', 0),
                                'liquidity': market.get('liquidity', 0),
                                'open_time': self._parse_datetime(market.get('createdTime')),
                                'close_time': self._parse_datetime(market.get('closeTime')),
                                'status': 'open' if not market.get('isResolved') else 'resolved',
                                'url': f"https://manifold.markets/{market.get('creatorUsername', '')}/{market.get('slug', '')}",
                                'last_updated': datetime.utcnow()
                            }
                            transformed_markets.append(transformed_market)
                        except Exception as e:
                            logger.error(f"Error transforming Manifold market: {e}")
                            continue
                    
                    logger.info(f"Retrieved {len(transformed_markets)} markets from Manifold")
                    return transformed_markets
                else:
                    logger.error(f"Manifold API request failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to fetch Manifold markets: {e}")
            return []
    
    def _get_outcomes(self, outcome_type: str) -> List[str]:
        """Get outcomes based on market type"""
        if outcome_type == 'BINARY':
            return ['Yes', 'No']
        elif outcome_type == 'FREE_RESPONSE':
            return ['Any answer']
        elif outcome_type == 'MULTIPLE_CHOICE':
            return ['Option A', 'Option B', 'Option C']  # Would need to fetch actual options
        else:
            return ['Yes', 'No']
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Manifold API"""
        if not date_str:
            return None
        
        try:
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse Manifold date {date_str}: {e}")
            return None

class RealPredictionMarketAggregator:
    """
    Aggregator for real prediction market APIs
    
    Integrates multiple real APIs and provides unified interface
    """
    
    def __init__(self, configs: Dict[str, APIConfig]):
        self.configs = configs
        self.clients = {}
        
    async def initialize_clients(self):
        """Initialize API clients"""
        for platform, config in self.configs.items():
            try:
                if platform == 'polymarket':
                    self.clients[platform] = PolymarketRealClient(config)
                elif platform == 'kalshi':
                    self.clients[platform] = KalshiRealClient(config)
                elif platform == 'manifold':
                    self.clients[platform] = ManifoldRealClient(config)
                elif platform == 'polyrouter':
                    # Use the PolyRouter client
                    self.clients[platform] = create_polyrouter_client(config.api_key)
                    if self.clients[platform] is None:
                        logger.warning("Failed to create PolyRouter client - no API key")
                        continue
                elif platform == 'dflow':
                    # Import DFlow client dynamically
                    try:
                        from dflow_client import DFlowAPIClient, DFlowConfig
                        dflow_config = DFlowConfig(
                            api_key=config.api_key,
                            base_url=config.base_url,
                            rate_limit=config.rate_limit,
                            timeout=config.timeout,
                            retry_attempts=config.retry_attempts,
                            retry_delay=config.retry_delay
                        )
                        self.clients[platform] = DFlowAPIClient(dflow_config)
                    except ImportError:
                        logger.warning("DFlow client not available, skipping")
                        continue
                elif platform == 'news':
                    self.clients[platform] = NewsAPIClient(config)
                else:
                    logger.warning(f"Unknown platform: {platform}")

                logger.info(f"Initialized client for {platform}")

            except Exception as e:
                logger.error(f"Failed to initialize {platform} client: {e}")
    
    async def get_all_markets(self, category: Optional[str] = None, limit_per_platform: int = 50) -> List[Dict]:
        """Get markets from all configured real platforms"""
        all_markets = []
        
        # Create tasks for concurrent API calls
        tasks = []
        for platform, client in self.clients.items():
            if platform != 'news':  # News is not a market platform
                task = self._get_markets_safe(client, category, limit_per_platform)
                tasks.append((platform, task))
        
        # Execute all requests concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for (platform, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch markets from {platform}: {result}")
                continue
            
            markets = result
            for market in markets:
                market['platform'] = platform  # Ensure platform is set
            
            all_markets.extend(markets)
        
        # Sort by volume (descending)
        all_markets.sort(key=lambda x: x.get('volume_24h', 0), reverse=True)
        
        logger.info(f"Aggregated {len(all_markets)} markets from {len(self.clients)} platforms")
        return all_markets
    
    async def _get_markets_safe(self, client, category: Optional[str], limit: int) -> List[Dict]:
        """Safely get markets from a client"""
        try:
            async with client:
                # Handle different client types
                if hasattr(client, '__class__'):
                    client_name = client.__class__.__name__

                    # PolyRouter has different signature
                    if client_name == 'PolyRouterClient':
                        # PolyRouter expects categories as a list
                        categories = [category] if category else None
                        return await client.get_markets(categories=categories, limit=limit)

                    # DFlow doesn't have get_markets - skip it
                    elif client_name == 'DFlowAPIClient':
                        logger.info("Skipping DFlow client for market data (trading-only client)")
                        return []

                    # Standard clients (Polymarket, Kalshi, Manifold)
                    else:
                        return await client.get_markets(category, limit)

                # Fallback to standard call
                return await client.get_markets(category, limit)

        except Exception as e:
            logger.error(f"Error getting markets from client: {e}")
            return []
    
    async def get_market_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """Get news related to a market query"""
        news_client = self.clients.get('news')
        if news_client:
            try:
                async with news_client:
                    return await news_client.get_market_news(query, days_back)
            except Exception as e:
                logger.error(f"Error getting market news: {e}")
        
        return []
    
    async def cleanup(self):
        """Cleanup all clients"""
        # Note: Context managers handle cleanup automatically
        logger.info("Real prediction market aggregator cleaned up")

# Configuration and testing functions
def create_api_configs() -> Dict[str, APIConfig]:
    """Create API configurations from environment variables or defaults"""
    import os

    configs = {}

    # Polymarket configuration
    polymarket_key = os.getenv('POLYMARKET_API_KEY', '')
    if polymarket_key:
        configs['polymarket'] = APIConfig(
            api_key=polymarket_key,
            base_url='https://gamma-api.polymarket.com',
            rate_limit=60
        )

    # Kalshi configuration
    kalshi_key = os.getenv('KALSHI_API_KEY', '')
    kalshi_secret = os.getenv('KALSHI_SECRET_KEY', '')
    if kalshi_key:
        configs['kalshi'] = APIConfig(
            api_key=kalshi_key,
            secret_key=kalshi_secret,
            base_url='https://trading-api.kalshi.com/v2',
            rate_limit=100
        )

    # Manifold configuration
    manifold_key = os.getenv('MANIFOLD_API_KEY', '')
    if manifold_key:
        configs['manifold'] = APIConfig(
            api_key=manifold_key,
            base_url='https://api.manifold.markets/v0',
            rate_limit=60
        )

    # PolyRouter configuration (Multi-platform aggregator)
    polyrouter_key = os.getenv('POLYROUTER_API_KEY', '')
    if polyrouter_key:
        configs['polyrouter'] = APIConfig(
            api_key=polyrouter_key,
            base_url='https://api.polyrouter.io/functions/v1',
            rate_limit=10  # PolyRouter has 10 req/sec limit in open beta
        )
        logger.info("PolyRouter API integration enabled")
    else:
        logger.info("PolyRouter API key not found - add POLYROUTER_API_KEY to enable unified platform access")

    # DFlow configuration (Solana prediction markets)
    dflow_key = os.getenv('DFLOW_API_KEY', '')
    # DFlow may work without API key for public endpoints
    configs['dflow'] = APIConfig(
        api_key=dflow_key if dflow_key else '',
        base_url='https://pond.dflow.net/api',
        rate_limit=100
    )

    # News API configuration
    news_api_key = os.getenv('NEWS_API_KEY', '')
    if news_api_key:
        configs['news'] = APIConfig(
            api_key=news_api_key,
            base_url='https://newsapi.org/v2',
            rate_limit=1000
        )

    return configs

async def test_real_apis():
    """Test real API clients"""
    print("Testing Real Prediction Market API Clients...")
    
    configs = create_api_configs()
    
    if not configs:
        print("No API keys found in environment variables.")
        print("Please set:")
        print("  POLYMARKET_API_KEY")
        print("  KALSHI_API_KEY, KALSHI_SECRET_KEY")
        print("  MANIFOLD_API_KEY")
        print("  POLYROUTER_API_KEY (for unified multi-platform access)")
        print("  NEWS_API_KEY")
        return
    
    aggregator = RealPredictionMarketAggregator(configs)
    await aggregator.initialize_clients()
    
    try:
        # Test market data fetching
        markets = await aggregator.get_all_markets(limit_per_platform=10)
        print(f"Retrieved {len(markets)} markets from real APIs")
        
        # Show sample market
        if markets:
            sample = markets[0]
            print(f"Sample market: {sample['question']} ({sample['platform']}) - ${sample.get('current_price', 'N/A')}")
        
        # Test news API
        if 'news' in aggregator.clients:
            news = await aggregator.get_market_news("Bitcoin price prediction", days_back=3)
            print(f"Retrieved {len(news)} news articles")
    
    finally:
        await aggregator.cleanup()
    
    print("Real API client testing completed!")

if __name__ == "__main__":
    asyncio.run(test_real_apis())