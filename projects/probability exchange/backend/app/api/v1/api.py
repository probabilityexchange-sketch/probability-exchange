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

from api_clients import (
    PredictionMarketAggregator, 
    MarketData, 
    PolymarketClient, 
    KalshiClient, 
    ManifoldClient,
    OrderRequest,
    OrderResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API router
api_router = APIRouter()

# Global aggregator instance (will be initialized on startup)
market_aggregator = None

async def get_market_aggregator() -> PredictionMarketAggregator:
    """Dependency to get the market aggregator instance"""
    global market_aggregator
    if market_aggregator is None:
        await initialize_aggregator()
    return market_aggregator

async def initialize_aggregator():
    """Initialize the prediction market aggregator with mock clients for demo"""
    global market_aggregator
    if market_aggregator is not None:
        return
    
    logger.info("Initializing Prediction Market Aggregator...")
    
    # Create aggregator instance
    market_aggregator = PredictionMarketAggregator()
    
    # For demo purposes, add mock clients (in production, use real API keys)
    # polymarket_client = PolymarketClient(api_key="demo_key", base_url="https://gamma-api.polymarket.com")
    # kalshi_client = KalshiClient(api_key="demo_key", base_url="https://trading-api.kalshi.com/v2")
    # manifold_client = ManifoldClient(api_key="demo_key", base_url="https://api.manifold.markets/v0")
    
    # For demo, we'll create a mock client that returns sample data
    class MockClient:
        async def get_markets(self, category=None, limit=50):
            """Return mock market data for demo"""
            return [
                MarketData(
                    id=f"market_{i}",
                    platform="polymarket",
                    question=f"Will {['Bitcoin', 'Ethereum', 'Apple Stock', 'Gold', 'Oil'][i % 5]} increase by 10% this week?",
                    description=f"Market about {['Bitcoin', 'Ethereum', 'Apple Stock', 'Gold', 'Oil'][i % 5]} price movement",
                    category="crypto" if i % 2 == 0 else "stocks",
                    current_price=0.45 + (i % 20) * 0.02,
                    probability=0.45 + (i % 20) * 0.02,
                    volume_24h=1000 + (i * 150),
                    total_volume=5000 + (i * 300),
                    liquidity=800 + (i * 100),
                    status="open",
                    last_updated=datetime.utcnow()
                )
                for i in range(limit)
            ]
        
        async def get_market(self, market_id):
            """Return mock market detail"""
            return MarketData(
                id=market_id,
                platform="polymarket", 
                question="Will Bitcoin increase by 10% this week?",
                description="Market about Bitcoin price movement",
                category="crypto",
                current_price=0.67,
                probability=0.67,
                volume_24h=2500,
                total_volume=10000,
                liquidity=2000,
                status="open",
                last_updated=datetime.utcnow()
            )
    
    # Add mock client to aggregator
    market_aggregator.add_client("polymarket", MockClient())
    
    logger.info("Market Aggregator initialized with mock data")

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
        self.market_updates = asyncio.create_task(self._broadcast_market_updates())
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
    
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
                # Simulate market data updates
                if market_aggregator:
                    await self._send_mock_updates()
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in market updates broadcast: {e}")
                await asyncio.sleep(5)
    
    async def _send_mock_updates(self):
        """Send mock market updates for demo"""
        # Generate random market update
        import random
        market_ids = [f"market_{i}" for i in range(20)]
        market_id = random.choice(market_ids)
        
        # Simulate price movement
        price_change = random.uniform(-0.05, 0.05)
        new_price = max(0.01, min(0.99, 0.5 + price_change))
        
        update = {
            "id": market_id,
            "platform": "polymarket",
            "current_price": new_price,
            "probability": new_price,
            "volume_24h": 1000 + random.randint(0, 500),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_market_update(update)

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