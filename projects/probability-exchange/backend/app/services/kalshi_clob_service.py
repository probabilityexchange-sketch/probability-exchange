#!/usr/bin/env python3
"""
Kalshi CLOB API Service

Fetches real-time market data from Kalshi's public API
Uses multiple endpoints with fallback support
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Kalshi API configurations - try multiple endpoints
KALSHI_ENDPOINTS = [
    "https://api.elections.kalshi.com/trade-api/v2",  # Elections API (public)
    "https://demo-api.kalshi.co/trade-api/v2",        # Demo API
    "https://api.kalshi.com/trade-api/v2",            # Production API
]


class KalshiCLOBService:
    """Service for fetching market data from Kalshi API"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.working_endpoint: Optional[str] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _find_working_endpoint(self) -> Optional[str]:
        """Try each endpoint to find one that works"""
        if self.working_endpoint:
            return self.working_endpoint

        for endpoint in KALSHI_ENDPOINTS:
            try:
                async with self.session.get(
                    f"{endpoint}/markets",
                    params={"limit": 1},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("markets") or data.get("cursor"):
                            self.working_endpoint = endpoint
                            logger.info(f"Found working Kalshi endpoint: {endpoint}")
                            return endpoint
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} failed: {e}")
                continue

        logger.warning("No working Kalshi endpoint found")
        return None

    async def fetch_markets(
        self,
        limit: int = 100,
        active_only: bool = True,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch markets from Kalshi API

        Args:
            limit: Maximum number of markets to return
            active_only: Only return markets that are currently open/active
            category: Filter by category (e.g., 'politics', 'sports', 'crypto', 'economics')

        Returns:
            List of market data dictionaries
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            endpoint = await self._find_working_endpoint()
            if not endpoint:
                return []

            params = {"limit": min(limit, 200)}
            if active_only:
                params["status"] = "open"

            async with self.session.get(
                f"{endpoint}/markets",
                params=params,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Kalshi API error: {resp.status}")
                    return []

                data = await resp.json()
                markets = data.get("markets", [])

                # Filter by category if specified
                if category:
                    markets = [m for m in markets if m.get("category", "").lower() == category.lower()]

                # Sort by volume
                markets.sort(key=lambda x: x.get("volume", 0) or 0, reverse=True)

                logger.info(f"Fetched {len(markets)} markets from Kalshi API")
                return markets[:limit]

        except asyncio.TimeoutError:
            logger.error("Kalshi API timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching markets from Kalshi: {e}")
            return []

    async def get_market_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get a specific market by ticker"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            endpoint = await self._find_working_endpoint()
            if not endpoint:
                return None

            async with self.session.get(
                f"{endpoint}/markets/{ticker}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()
                return data.get("market") if isinstance(data, dict) else data

        except Exception as e:
            logger.error(f"Error fetching market {ticker}: {e}")
            return None

    def format_market_for_api(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Kalshi market format to standard API format"""
        # Kalshi uses 'yes' and 'no' outcomes typically
        outcomes = ["yes", "no"]

        # Get the yes price (probability)
        yes_price = market.get("yes_price", 50) / 100.0  # Kalshi uses 0-100 scale
        probability = yes_price

        return {
            "id": market.get("ticker", ""),
            "platform": "kalshi",
            "question": market.get("title", ""),
            "description": market.get("description", ""),
            "category": market.get("category", "General"),
            "market_type": market.get("type", "binary"),
            "outcomes": outcomes,
            "current_price": probability,
            "probability": probability,
            "volume_24h": market.get("volume_24h", 0) or 0,
            "total_volume": market.get("total_volume", 0) or 0,
            "liquidity": market.get("liquidity", 0) or 0,
            "status": market.get("status", "unknown"),
            "url": f"https://kalshi.com/markets/{market.get('ticker', '')}",
            "open_time": market.get("open_time"),
            "close_time": market.get("close_time"),
            "last_updated": datetime.utcnow().isoformat(),
            "source": "kalshi_clob",
            "raw_data": market,
            "ticker": market.get("ticker", ""),
        }


# Global service instance
_kalshi_service: Optional[KalshiCLOBService] = None


async def get_kalshi_service() -> KalshiCLOBService:
    """Get or create Kalshi service instance"""
    global _kalshi_service
    if _kalshi_service is None:
        _kalshi_service = KalshiCLOBService()
    return _kalshi_service
