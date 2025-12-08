#!/usr/bin/env python3
"""
Polymarket CLOB API Service

Fetches real-time market data from Polymarket's public CLOB API
No authentication required - read-only public data
"""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Polymarket CLOB API configuration
CLOB_BASE_URL = "https://clob.polymarket.com"


class PolymarketCLOBService:
    """Service for fetching market data from Polymarket CLOB API"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_markets(
        self,
        limit: int = 100,
        active_only: bool = True,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch markets from Polymarket CLOB API

        Args:
            limit: Maximum number of markets to return
            active_only: Only return markets that are currently accepting orders (default True)
            category: Filter by category (e.g., 'Politics', 'Crypto', 'Sports')

        Returns:
            List of market data dictionaries sorted by volume (highest first)
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(f"{CLOB_BASE_URL}/markets", timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.error(f"CLOB API error: {resp.status}")
                    return []

                data = await resp.json()
                markets = data if isinstance(data, list) else data.get("data", [])

                # Filter markets
                filtered_markets = []
                for market in markets:
                    # Skip closed/resolved markets if active_only
                    if active_only:
                        if market.get("closed", False):
                            continue
                        if not market.get("accepting_orders", False):
                            continue
                        if market.get("archived", False):
                            continue

                    # Skip if category specified and doesn't match
                    if category and market.get("category", "").lower() != category.lower():
                        continue

                    filtered_markets.append(market)

                # Sort by volume (highest first) to get most active markets
                filtered_markets.sort(
                    key=lambda x: float(x.get("volume", 0) or 0),
                    reverse=True
                )

                # Apply limit after sorting
                result = filtered_markets[:limit]

                logger.info(f"Fetched {len(result)} active markets from CLOB API (filtered from {len(markets)} total)")
                return result

        except asyncio.TimeoutError:
            logger.error("CLOB API timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching markets from CLOB: {e}")
            return []

    async def get_market_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get a specific market by slug"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(f"{CLOB_BASE_URL}/markets", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None

                data = await resp.json()
                markets = data.get("data", []) if isinstance(data, dict) else data

                for market in markets:
                    if market.get("market_slug") == slug:
                        return market

                return None

        except Exception as e:
            logger.error(f"Error fetching market {slug}: {e}")
            return None

    def format_market_for_api(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CLOB market format to standard API format"""
        tokens = market.get("tokens", [])
        outcomes = [t.get("outcome", "Unknown") for t in tokens]
        prices = [t.get("price", 0) for t in tokens]

        # Calculate probability from first outcome (Yes/No binary market)
        probability = prices[0] if prices else 0.5

        return {
            "id": market.get("condition_id", market.get("question_id", "")),
            "platform": "polymarket",
            "question": market.get("question", ""),
            "description": market.get("description", ""),
            "category": market.get("category", "General"),
            "market_type": market.get("market_type", "normal"),
            "outcomes": outcomes,
            "current_price": probability,
            "probability": probability,
            "volume_24h": market.get("volume24hr", 0) or 0,
            "total_volume": market.get("volume", 0) or 0,
            "liquidity": market.get("liquidity", 0) or 0,
            "status": "resolved" if market.get("closed") else "open",
            "url": f"https://polymarket.com/market/{market.get('market_slug', '')}",
            "open_time": market.get("createdAt"),
            "close_time": market.get("endDate"),
            "last_updated": datetime.utcnow().isoformat(),
            "source": "polymarket_clob",
            "raw_data": market,
            "accepting_orders": market.get("accepting_orders", False),
            "market_slug": market.get("market_slug", ""),
        }


# Global service instance
_clob_service: Optional[PolymarketCLOBService] = None


async def get_clob_service() -> PolymarketCLOBService:
    """Get or create CLOB service instance"""
    global _clob_service
    if _clob_service is None:
        _clob_service = PolymarketCLOBService()
    return _clob_service
