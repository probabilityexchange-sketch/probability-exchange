#!/usr/bin/env python3
"""
API v1 Router for MarketPulse Pro

This module contains all API v1 routes including market data endpoints,
real-time updates via WebSockets, and aggregation services.
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Any
import asyncio
import logging
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client_integration import (
    PredictionMarketAggregator,
    MarketData,
    PolymarketRealClient,
    KalshiRealClient,
    ManifoldRealClient,
    OrderRequest,
    OrderResponse,
    APIConfig,
    MockMarketClient
)

# Legacy client class names for backward compatibility
class PolymarketClient:
    def __init__(self, api_key: str = "", base_url: str = ""):
        config = APIConfig(
            api_key=api_key or settings.POLYMARKET_API_KEY or "",
            base_url=base_url or "https://gamma-api.polymarket.com",
            rate_limit=60
        )
        self._client = PolymarketRealClient(config)
    
    async def get_markets(self, category=None, limit=50):
        try:
            async with self._client:
                return await self._client.get_markets(category, limit)
        except Exception as e:
            logger.error(f"Error fetching Polymarket markets: {e}")
            return []

class KalshiClient:
    def __init__(self, api_key: str = "", base_url: str = ""):
        config = APIConfig(
            api_key=api_key or settings.KALSHI_API_KEY or "",
            secret_key=settings.KALSHI_SECRET_KEY or None,
            base_url=base_url or "https://trading-api.kalshi.com/v2",
            rate_limit=100
        )
        self._client = KalshiRealClient(config)
    
    async def get_markets(self, category=None, limit=50):
        try:
            async with self._client:
                return await self._client.get_markets(category, limit)
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []

class ManifoldClient:
    def __init__(self, api_key: str = "", base_url: str = ""):
        config = APIConfig(
            api_key=api_key or settings.MANIFOLD_API_KEY or "",
            base_url=base_url or "https://api.manifold.markets/v0",
            rate_limit=60
        )
        self._client = ManifoldRealClient(config)
    
    async def get_markets(self, category=None, limit=50):
        try:
            async with self._client:
                return await self._client.get_markets(category, limit)
        except Exception as e:
            logger.error(f"Error fetching Manifold markets: {e}")
            return []
from app.core.config_simple import settings

# Import wallet authentication router
# TODO: Enable after web3_wallets module is created
# from .wallet_auth import wallet_router

# Import news router
from .news import news_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API router
api_router = APIRouter()

# Include news routes
api_router.include_router(news_router, tags=["news"])

# Global aggregator instance (will be initialized on startup)
market_aggregator: Optional[PredictionMarketAggregator] = None

async def get_market_aggregator() -> PredictionMarketAggregator:
    """Dependency to get the market aggregator instance"""
    global market_aggregator
    if market_aggregator is None:
        await initialize_aggregator()
    if market_aggregator is None:
        raise HTTPException(status_code=500, detail="Market aggregator not initialized")
    return market_aggregator

class MockMarketClient:
    """Mock client that returns sample market data for demo purposes"""

    def __init__(self, platform: str):
        self.platform = platform

    async def get_markets(self, category: Optional[str] = None, limit: int = 50) -> List[MarketData]:
        """Return mock market data"""
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
        """Get specific market by ID"""
        markets = await self.get_markets()
        for market in markets:
            if market.id == market_id:
                return market
        return None

async def initialize_aggregator():
    """Initialize the prediction market aggregator with API configurations"""
    global market_aggregator
    if market_aggregator is not None:
        return

    # Create API configurations for all platforms
    api_configs = {
        "kalshi": APIConfig(
            api_key=settings.KALSHI_API_KEY or "",
            base_url="https://trading-api.kalshi.com/v2",
            rate_limit=60,
            timeout=30
        ),
        "polymarket": APIConfig(
            api_key=settings.POLYMARKET_API_KEY or "",
            base_url="https://gamma-api.polymarket.com",
            rate_limit=60,
            timeout=30
        ),
        "manifold": APIConfig(
            api_key=settings.MANIFOLD_API_KEY or "",
            base_url="https://api.manifold.markets/v0",
            rate_limit=60,
            timeout=30
        ),
        "news": APIConfig(
            api_key="",  # News API key not configured yet, will use mock data
            base_url="https://newsapi.org/v2",
            rate_limit=100,
            timeout=30
        )
    }

    # Initialize aggregator with configs
    market_aggregator = PredictionMarketAggregator(api_configs)

    # Initialize all clients (real or mock based on API keys)
    await market_aggregator.initialize_clients()

    logger.info("Market Aggregator initialized successfully")

# Market endpoints
@api_router.get("/markets")
async def get_markets(
    category: Optional[str] = None,
    limit: int = 50,
    aggregator: PredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Get aggregated markets from all platforms"""
    try:
        markets = await aggregator.get_all_markets(
            category=category,
            limit_per_platform=limit // 3  # Divide limit across platforms
        )
        
        # Convert to dictionaries for JSON serialization
        return {
            "markets": [
                {
                    "id": market.id,
                    "platform": market.platform,
                    "question": market.question,
                    "description": market.description,
                    "category": market.category,
                    "market_type": market.market_type,
                    "outcomes": market.outcomes,
                    "current_price": market.current_price,
                    "probability": market.probability,
                    "volume_24h": market.volume_24h,
                    "total_volume": market.total_volume,
                    "liquidity": market.liquidity,
                    "status": market.status,
                    "url": market.url,
                    "last_updated": market.last_updated.isoformat() if market.last_updated else None
                }
                for market in markets[:limit]
            ],
            "total": len(markets),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/markets/{market_id}")
async def get_market_details(
    market_id: str,
    aggregator: PredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Get detailed information for a specific market"""
    try:
        # Try to find market in all platforms
        for platform, client in aggregator.clients.items():
            try:
                market = await client.get_market(market_id)
                if market:
                    return {
                        "id": market.id,
                        "platform": market.platform,
                        "question": market.question,
                        "description": market.description,
                        "category": market.category,
                        "market_type": market.market_type,
                        "outcomes": market.outcomes,
                        "current_price": market.current_price,
                        "probability": market.probability,
                        "volume_24h": market.volume_24h,
                        "total_volume": market.total_volume,
                        "liquidity": market.liquidity,
                        "open_time": market.open_time.isoformat() if market.open_time else None,
                        "close_time": market.close_time.isoformat() if market.close_time else None,
                        "resolution_date": market.resolution_date.isoformat() if market.resolution_date else None,
                        "status": market.status,
                        "url": market.url,
                        "last_updated": market.last_updated.isoformat() if market.last_updated else None
                    }
            except Exception as e:
                logger.error(f"Error fetching market {market_id} from {platform}: {e}")
                continue
        
        raise HTTPException(status_code=404, detail="Market not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/markets/compare")
async def compare_markets(
    question: str,
    aggregator: PredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Compare the same market across different platforms"""
    try:
        results = await aggregator.compare_market(question)
        
        return {
            "question": question,
            "platforms": {
                platform: {
                    "id": market.id if market else None,
                    "platform": market.platform if market else None,
                    "question": market.question if market else None,
                    "probability": market.probability if market else None,
                    "current_price": market.current_price if market else None,
                    "volume_24h": market.volume_24h if market else None,
                    "status": market.status if market else None,
                    "last_updated": market.last_updated.isoformat() if market and market.last_updated else None
                }
                for platform, market in results.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_updates_task = None
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

        # Start background task on first connection
        if self.market_updates_task is None:
            self.market_updates_task = asyncio.create_task(self._broadcast_market_updates())
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def broadcast_market_update(self, market_data: Dict):
        """Send market update to all connected clients"""
        if not self.active_connections:
            return
            
        message = {
            "type": "market_update",
            "data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send update to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def _broadcast_market_updates(self):
        """Background task to broadcast periodic market updates"""
        while True:
            try:
                if market_aggregator:
                    # Fetch real market updates
                    await self._send_real_updates()
                else:
                    logger.warning("Market aggregator not initialized, skipping updates")

                await asyncio.sleep(15)  # Polling interval (15 seconds to avoid rate limits)
            except Exception as e:
                logger.error(f"Error in market updates broadcast: {e}")
                await asyncio.sleep(15)
    
    async def _send_real_updates(self):
        """Fetch and broadcast real market updates"""
        try:
            # Fetch top markets from aggregator
            # We limit to small number per platform to respect rate limits during polling
            markets = await market_aggregator.get_all_markets(limit_per_platform=5)

            for market in markets:
                # Convert to dict for JSON serialization
                market_data = {
                    "id": market.id,
                    "platform": market.platform,
                    "question": market.question,
                    "description": market.description,
                    "category": market.category,
                    "market_type": market.market_type,
                    "outcomes": market.outcomes,
                    "current_price": market.current_price,
                    "probability": market.probability,
                    "volume_24h": market.volume_24h,
                    "total_volume": market.total_volume,
                    "liquidity": market.liquidity,
                    "status": market.status,
                    "url": market.url,
                    "last_updated": datetime.utcnow().isoformat()
                }

                await self.broadcast_market_update(market_data)
                # Small delay to avoid flooding clients
                await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"Error fetching real market updates: {e}")

# Global connection manager
manager = ConnectionManager()

@api_router.websocket("/ws/markets")
async def websocket_market_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time market updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            # Echo back for keepalive or handle client requests
            await websocket.send_text(json.dumps({
                "type": "ack",
                "timestamp": datetime.utcnow().isoformat()
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health and status endpoints
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "marketpulse-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "aggregator_initialized": market_aggregator is not None,
        "active_connections": len(manager.active_connections)
    }

@api_router.get("/status")
async def get_api_status(aggregator: PredictionMarketAggregator = Depends(get_market_aggregator)):
    """Get detailed API status and platform connectivity"""
    try:
        platforms = {}
        for platform, client in aggregator.clients.items():
            platforms[platform] = {
                "connected": True,
                "last_check": datetime.utcnow().isoformat(),
                "status": "active"
            }
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "platforms": platforms,
            "aggregator": {
                "clients_count": len(aggregator.clients),
                "initialized": True
            },
            "websocket": {
                "active_connections": len(manager.active_connections),
                "status": "active"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        raise HTTPException(status_code=500, detail=str(e))