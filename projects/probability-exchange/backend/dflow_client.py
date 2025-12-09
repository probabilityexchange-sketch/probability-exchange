#!/usr/bin/env python3
"""
DFlow API Client for Solana Prediction Markets Trading

This module implements integration with DFlow's pond.dflow.net API for:
- Tokenized Kalshi prediction markets on Solana
- Swap API (Imperative and Declarative modes)
- Order management and tracking
- SPL token trading for prediction market positions

References:
- DFlow API: https://pond.dflow.net/introduction
- Swap API: https://pond.dflow.net/swap-api-reference/introduction
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DFlowConfig:
    """Configuration for DFlow API client"""
    api_key: Optional[str] = None
    base_url: str = "https://pond.dflow.net/api"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit: int = 100


@dataclass
class SwapQuote:
    """DFlow swap quote response"""
    in_token: str
    out_token: str
    in_amount: str
    out_amount: str
    price_impact: float
    estimated_slippage: float
    route: List[Dict[str, Any]]
    expires_at: datetime


@dataclass
class MarketPosition:
    """Tokenized prediction market position"""
    market_id: str
    token_mint: str  # Solana SPL token mint address
    outcome: str
    shares: Decimal
    average_price: Decimal
    current_value: Decimal
    pnl: Decimal
    platform: str = "dflow"


class DFlowAPIClient:
    """
    DFlow API Client for Solana-based prediction market trading

    Provides access to tokenized Kalshi markets on Solana through DFlow's
    Concurrent Liquidity Programs (CLPs).
    """

    def __init__(self, config: DFlowConfig):
        self.config = config
        self.base_url = config.base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_bucket = asyncio.Semaphore(config.rate_limit // 60)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self._get_headers()
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for DFlow API"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MarketPulsePro/1.0',
            'Accept': 'application/json'
        }

        # Add API key if provided
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'

        return headers

    async def _rate_limited_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a rate-limited API request with retry logic"""
        async with self.rate_limit_bucket:
            for attempt in range(self.config.retry_attempts):
                try:
                    url = urljoin(self.base_url, endpoint)

                    async with self.session.request(method, url, **kwargs) as response:
                        # Handle rate limiting
                        if response.status == 429:
                            retry_after = int(response.headers.get('Retry-After', 60))
                            logger.warning(f"DFlow rate limit exceeded, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue

                        # Handle errors
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"DFlow API Error {response.status}: {error_text}")
                            raise aiohttp.ClientError(
                                f"DFlow API Error {response.status}: {error_text}"
                            )

                        return await response.json()

                except aiohttp.ClientError as e:
                    if attempt == self.config.retry_attempts - 1:
                        raise

                    logger.warning(f"DFlow request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

    # ============================================================================
    # Prediction Market Discovery
    # ============================================================================

    async def get_prediction_markets(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get available tokenized prediction markets from DFlow

        These are Kalshi markets available as SPL tokens on Solana.

        Args:
            category: Optional category filter (politics, sports, economics, etc.)
            limit: Maximum number of markets to return

        Returns:
            List of prediction market data
        """
        try:
            params = {'limit': min(limit, 200)}
            if category:
                params['category'] = category

            # Note: Adjust endpoint based on actual DFlow API documentation
            response = await self._rate_limited_request(
                'GET',
                '/prediction-markets',
                params=params
            )

            markets = response.get('markets', [])

            # Transform to consistent format
            transformed_markets = []
            for market in markets:
                try:
                    transformed_market = {
                        'id': market.get('id'),
                        'platform': 'dflow',
                        'chain': 'solana',
                        'question': market.get('title', ''),
                        'description': market.get('description'),
                        'category': market.get('category'),
                        'market_type': 'BINARY',  # Kalshi markets are binary
                        'outcomes': ['Yes', 'No'],

                        # Token information
                        'yes_token_mint': market.get('yesTokenMint'),
                        'no_token_mint': market.get('noTokenMint'),

                        # Pricing
                        'yes_price': float(market.get('yesPrice', 0)),
                        'no_price': float(market.get('noPrice', 0)),
                        'probability': float(market.get('probability', 0)),

                        # Volume and liquidity
                        'volume_24h': float(market.get('volume24h', 0)),
                        'total_volume': float(market.get('totalVolume', 0)),
                        'liquidity': float(market.get('liquidity', 0)),

                        # Dates
                        'open_time': self._parse_timestamp(market.get('openTime')),
                        'close_time': self._parse_timestamp(market.get('closeTime')),
                        'resolution_date': self._parse_timestamp(market.get('resolutionTime')),

                        # Status
                        'status': market.get('status', 'open'),
                        'is_settled': market.get('isSettled', False),

                        # Links
                        'url': market.get('url'),
                        'kalshi_url': market.get('kalshiUrl'),

                        'last_updated': datetime.utcnow()
                    }
                    transformed_markets.append(transformed_market)
                except Exception as e:
                    logger.error(f"Error transforming DFlow market: {e}")
                    continue

            logger.info(f"Retrieved {len(transformed_markets)} markets from DFlow")
            return transformed_markets

        except Exception as e:
            logger.error(f"Failed to fetch DFlow prediction markets: {e}")
            return []

    async def get_market_detail(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific prediction market

        Args:
            market_id: The market identifier

        Returns:
            Market detail data
        """
        try:
            response = await self._rate_limited_request(
                'GET',
                f'/prediction-markets/{market_id}'
            )

            market = response.get('market', response)

            return {
                'id': market.get('id'),
                'platform': 'dflow',
                'chain': 'solana',
                'question': market.get('title', ''),
                'description': market.get('description'),
                'category': market.get('category'),
                'yes_token_mint': market.get('yesTokenMint'),
                'no_token_mint': market.get('noTokenMint'),
                'yes_price': float(market.get('yesPrice', 0)),
                'no_price': float(market.get('noPrice', 0)),
                'probability': float(market.get('probability', 0)),
                'volume_24h': float(market.get('volume24h', 0)),
                'total_volume': float(market.get('totalVolume', 0)),
                'liquidity': float(market.get('liquidity', 0)),
                'status': market.get('status', 'open'),
                'url': market.get('url'),
                'last_updated': datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Failed to fetch DFlow market {market_id}: {e}")
            return None

    # ============================================================================
    # Trading - Swap API
    # ============================================================================

    async def get_swap_quote(
        self,
        input_token: str,
        output_token: str,
        amount: str,
        slippage_tolerance: float = 0.01  # 1% default
    ) -> Optional[SwapQuote]:
        """
        Get a quote for swapping tokens (e.g., USDC -> YES token)

        Args:
            input_token: Input token mint address (e.g., USDC)
            output_token: Output token mint address (e.g., YES token)
            amount: Amount of input token (in smallest units)
            slippage_tolerance: Maximum acceptable slippage (0.01 = 1%)

        Returns:
            SwapQuote object with pricing and route information
        """
        try:
            params = {
                'inputMint': input_token,
                'outputMint': output_token,
                'amount': amount,
                'slippageBps': int(slippage_tolerance * 10000)  # Convert to basis points
            }

            response = await self._rate_limited_request(
                'GET',
                '/quote',
                params=params
            )

            return SwapQuote(
                in_token=response['inToken'],
                out_token=response['outToken'],
                in_amount=response['inAmount'],
                out_amount=response['outAmount'],
                price_impact=float(response.get('priceImpact', 0)),
                estimated_slippage=float(response.get('estimatedSlippage', 0)),
                route=response.get('route', []),
                expires_at=self._parse_timestamp(response.get('expiresAt'))
            )

        except Exception as e:
            logger.error(f"Failed to get swap quote: {e}")
            return None

    async def execute_swap_imperative(
        self,
        quote: SwapQuote,
        user_public_key: str,
        priority_fee: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a swap using imperative mode (full control over transaction)

        Args:
            quote: SwapQuote from get_swap_quote()
            user_public_key: User's Solana wallet public key
            priority_fee: Optional priority fee in lamports

        Returns:
            Transaction data for signing
        """
        try:
            payload = {
                'inputMint': quote.in_token,
                'outputMint': quote.out_token,
                'amount': quote.in_amount,
                'userPublicKey': user_public_key,
                'slippageBps': int(quote.estimated_slippage * 10000)
            }

            if priority_fee:
                payload['priorityFee'] = priority_fee

            response = await self._rate_limited_request(
                'POST',
                '/swap',
                json=payload
            )

            return {
                'transaction': response.get('transaction'),
                'swap_id': response.get('swapId'),
                'status': response.get('status'),
                'message': response.get('message')
            }

        except Exception as e:
            logger.error(f"Failed to execute imperative swap: {e}")
            raise

    async def execute_swap_declarative(
        self,
        input_token: str,
        output_token: str,
        amount: str,
        user_public_key: str,
        slippage_tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Execute a swap using declarative mode (deferred route calculation)

        Declarative mode provides better slippage protection and sandwich attack
        resistance through multi-transaction intent submission.

        Args:
            input_token: Input token mint address
            output_token: Output token mint address
            amount: Amount of input token
            user_public_key: User's Solana wallet public key
            slippage_tolerance: Maximum acceptable slippage

        Returns:
            Intent submission result
        """
        try:
            payload = {
                'inputMint': input_token,
                'outputMint': output_token,
                'amount': amount,
                'userPublicKey': user_public_key,
                'slippageBps': int(slippage_tolerance * 10000)
            }

            response = await self._rate_limited_request(
                'POST',
                '/submit-intent',
                json=payload
            )

            return {
                'intent_id': response.get('intentId'),
                'status': response.get('status'),
                'estimated_completion': response.get('estimatedCompletion'),
                'message': response.get('message')
            }

        except Exception as e:
            logger.error(f"Failed to execute declarative swap: {e}")
            raise

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of a swap order

        Args:
            order_id: The order ID from swap execution

        Returns:
            Order status information
        """
        try:
            response = await self._rate_limited_request(
                'GET',
                f'/order-status',
                params={'orderId': order_id}
            )

            return {
                'order_id': response.get('orderId'),
                'status': response.get('status'),
                'fill_price': response.get('fillPrice'),
                'filled_amount': response.get('filledAmount'),
                'transaction_signature': response.get('txSignature'),
                'timestamp': self._parse_timestamp(response.get('timestamp'))
            }

        except Exception as e:
            logger.error(f"Failed to get order status for {order_id}: {e}")
            return {}

    # ============================================================================
    # Token & Venue Information
    # ============================================================================

    async def get_available_tokens(
        self,
        include_decimals: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get list of available tokens for trading

        Args:
            include_decimals: Whether to include decimal information

        Returns:
            List of available tokens
        """
        try:
            endpoint = '/tokens-with-decimals' if include_decimals else '/tokens'

            response = await self._rate_limited_request('GET', endpoint)

            return response.get('tokens', [])

        except Exception as e:
            logger.error(f"Failed to get available tokens: {e}")
            return []

    async def get_trading_venues(self) -> List[Dict[str, Any]]:
        """
        Get list of liquidity venues available through DFlow

        Returns:
            List of trading venues
        """
        try:
            response = await self._rate_limited_request('GET', '/venues')

            return response.get('venues', [])

        except Exception as e:
            logger.error(f"Failed to get trading venues: {e}")
            return []

    # ============================================================================
    # Portfolio Management
    # ============================================================================

    async def get_user_positions(
        self,
        wallet_address: str
    ) -> List[MarketPosition]:
        """
        Get user's prediction market positions

        Fetches all tokenized prediction market positions held by a wallet.

        Args:
            wallet_address: Solana wallet address

        Returns:
            List of MarketPosition objects
        """
        try:
            response = await self._rate_limited_request(
                'GET',
                '/user/positions',
                params={'wallet': wallet_address}
            )

            positions = []
            for pos in response.get('positions', []):
                try:
                    position = MarketPosition(
                        market_id=pos['marketId'],
                        token_mint=pos['tokenMint'],
                        outcome=pos['outcome'],
                        shares=Decimal(str(pos['shares'])),
                        average_price=Decimal(str(pos['averagePrice'])),
                        current_value=Decimal(str(pos['currentValue'])),
                        pnl=Decimal(str(pos['pnl']))
                    )
                    positions.append(position)
                except Exception as e:
                    logger.error(f"Error parsing position: {e}")
                    continue

            return positions

        except Exception as e:
            logger.error(f"Failed to get user positions: {e}")
            return []

    async def get_wallet_balance(
        self,
        wallet_address: str,
        token_mint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get wallet token balances

        Args:
            wallet_address: Solana wallet address
            token_mint: Optional specific token mint to query

        Returns:
            Balance information
        """
        try:
            params = {'wallet': wallet_address}
            if token_mint:
                params['tokenMint'] = token_mint

            response = await self._rate_limited_request(
                'GET',
                '/user/balance',
                params=params
            )

            return response

        except Exception as e:
            logger.error(f"Failed to get wallet balance: {e}")
            return {}

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def _parse_timestamp(self, timestamp: Optional[Any]) -> Optional[datetime]:
        """Parse timestamp from API response"""
        if not timestamp:
            return None

        try:
            # Handle Unix timestamp (milliseconds or seconds)
            if isinstance(timestamp, (int, float)):
                # If timestamp is too large, it's likely in milliseconds
                if timestamp > 10000000000:
                    timestamp = timestamp / 1000
                return datetime.fromtimestamp(timestamp)

            # Handle ISO string
            if isinstance(timestamp, str):
                if timestamp.endswith('Z'):
                    timestamp = timestamp[:-1] + '+00:00'
                return datetime.fromisoformat(timestamp)

            return None

        except Exception as e:
            logger.warning(f"Failed to parse timestamp {timestamp}: {e}")
            return None

    async def health_check(self) -> bool:
        """Check if DFlow API is accessible"""
        try:
            response = await self._rate_limited_request('GET', '/health')
            return response.get('status') == 'ok'
        except Exception:
            return False


# ============================================================================
# Configuration Helper
# ============================================================================

def create_dflow_config() -> Optional[DFlowConfig]:
    """Create DFlow configuration from environment variables"""
    import os

    api_key = os.getenv('DFLOW_API_KEY')

    # DFlow may not require API key for public endpoints
    config = DFlowConfig(
        api_key=api_key,
        base_url=os.getenv('DFLOW_BASE_URL', 'https://pond.dflow.net/api'),
        rate_limit=int(os.getenv('DFLOW_RATE_LIMIT', '100'))
    )

    return config


# ============================================================================
# Testing
# ============================================================================

async def test_dflow_client():
    """Test DFlow API client functionality"""
    print("Testing DFlow API Client...")

    config = create_dflow_config()

    async with DFlowAPIClient(config) as client:
        # Test health check
        print("\n1. Testing health check...")
        is_healthy = await client.health_check()
        print(f"   API Health: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")

        # Test market discovery
        print("\n2. Testing prediction market discovery...")
        markets = await client.get_prediction_markets(limit=5)
        print(f"   Found {len(markets)} markets")

        if markets:
            sample = markets[0]
            print(f"   Sample: {sample['question'][:60]}...")
            print(f"   YES Price: ${sample.get('yes_price', 'N/A')}")
            print(f"   NO Price: ${sample.get('no_price', 'N/A')}")

        # Test token listing
        print("\n3. Testing token listing...")
        tokens = await client.get_available_tokens()
        print(f"   Found {len(tokens)} available tokens")

        # Test venues
        print("\n4. Testing trading venues...")
        venues = await client.get_trading_venues()
        print(f"   Found {len(venues)} liquidity venues")

    print("\n✓ DFlow API client testing completed!")


if __name__ == "__main__":
    asyncio.run(test_dflow_client())
