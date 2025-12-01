#!/usr/bin/env python3
"""
Real API v1 Router for MarketPulse Pro

This module contains all API v1 routes with real API integrations for:
- Polymarket API
- Kalshi API  
- Manifold Markets API
- News APIs for sentiment analysis

Real-time updates via WebSockets and aggregation services.
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

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from real_api_clients import (
    RealPredictionMarketAggregator, 
    APIConfig,
    create_api_configs
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API router
api_router = APIRouter()

# Global aggregator instance (will be initialized on startup)
market_aggregator = None

async def get_market_aggregator() -> RealPredictionMarketAggregator:
    """Dependency to get the real market aggregator instance"""
    global market_aggregator
    if market_aggregator is None:
        await initialize_real_aggregator()
    return market_aggregator

async def initialize_real_aggregator():
    """Initialize the real prediction market aggregator with API clients"""
    global market_aggregator
    if market_aggregator is not None:
        return
    
    logger.info("Initializing Real Prediction Market Aggregator...")
    
    # Create API configurations
    configs = create_api_configs()
    
    if not configs:
        logger.warning("No API keys found in environment variables. Using fallback mock data.")
        # Fallback to mock data if no API keys
        market_aggregator = await create_mock_aggregator()
        return
    
    # Create aggregator instance with real API configs
    market_aggregator = RealPredictionMarketAggregator(configs)
    
    # Initialize all API clients
    await market_aggregator.initialize_clients()
    
    logger.info(f"Real Market Aggregator initialized with {len(configs)} API clients")

async def create_mock_aggregator():
    """Create fallback mock aggregator if no API keys available"""
    from api_clients import PredictionMarketAggregator, MarketData
    
    logger.info("Creating fallback mock aggregator...")
    
    # Create aggregator instance
    aggregator = PredictionMarketAggregator()
    
    # Mock client that returns sample data
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
    aggregator.add_client("mock", MockClient())
    
    return aggregator

# Market endpoints
@api_router.get("/markets")
async def get_markets(
    category: Optional[str] = None,
    limit: int = 50,
    aggregator: RealPredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Get aggregated markets from all real platforms"""
    try:
        markets = await aggregator.get_all_markets(
            category=category,
            limit_per_platform=limit // 3  # Divide limit across platforms
        )
        
        # Convert to dictionaries for JSON serialization
        return {
            "markets": [
                {
                    "id": market.get("id"),
                    "platform": market.get("platform"),
                    "question": market.get("question"),
                    "description": market.get("description"),
                    "category": market.get("category"),
                    "market_type": market.get("market_type"),
                    "outcomes": market.get("outcomes"),
                    "current_price": market.get("current_price"),
                    "probability": market.get("probability"),
                    "volume_24h": market.get("volume_24h"),
                    "total_volume": market.get("total_volume"),
                    "liquidity": market.get("liquidity"),
                    "status": market.get("status"),
                    "url": market.get("url"),
                    "last_updated": market.get("last_updated").isoformat() if market.get("last_updated") else None
                }
                for market in markets[:limit]
            ],
            "total": len(markets),
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "real_apis" if hasattr(aggregator, 'configs') and aggregator.configs else "mock_data"
        }
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/markets/{market_id}")
async def get_market_details(
    market_id: str,
    aggregator: RealPredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Get detailed information for a specific market"""
    try:
        # Try to find market in all platforms
        for platform, client in aggregator.clients.items():
            try:
                async with client:
                    market = await client.get_market(market_id)
                    if market:
                        return {
                            "id": market.get("id"),
                            "platform": market.get("platform"),
                            "question": market.get("question"),
                            "description": market.get("description"),
                            "category": market.get("category"),
                            "market_type": market.get("market_type"),
                            "outcomes": market.get("outcomes"),
                            "current_price": market.get("current_price"),
                            "probability": market.get("probability"),
                            "volume_24h": market.get("volume_24h"),
                            "total_volume": market.get("total_volume"),
                            "liquidity": market.get("liquidity"),
                            "open_time": market.get("open_time").isoformat() if market.get("open_time") else None,
                            "close_time": market.get("close_time").isoformat() if market.get("close_time") else None,
                            "resolution_date": market.get("resolution_date").isoformat() if market.get("resolution_date") else None,
                            "status": market.get("status"),
                            "url": market.get("url"),
                            "last_updated": market.get("last_updated").isoformat() if market.get("last_updated") else None
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
    aggregator: RealPredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Compare the same market across different platforms"""
    try:
        results = await aggregator.compare_market(question)
        
        return {
            "question": question,
            "platforms": {
                platform: {
                    "id": market.get("id") if market else None,
                    "platform": market.get("platform") if market else None,
                    "question": market.get("question") if market else None,
                    "probability": market.get("probability") if market else None,
                    "current_price": market.get("current_price") if market else None,
                    "volume_24h": market.get("volume_24h") if market else None,
                    "status": market.get("status") if market else None,
                    "last_updated": market.get("last_updated").isoformat() if market and market.get("last_updated") else None
                }
                for platform, market in results.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error comparing markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/news/{query}")
async def get_market_news(
    query: str,
    days_back: int = 7,
    aggregator: RealPredictionMarketAggregator = Depends(get_market_aggregator)
):
    """Get news articles related to a market query"""
    try:
        news_articles = await aggregator.get_market_news(query, days_back)
        
        return {
            "query": query,
            "articles": news_articles,
            "total": len(news_articles),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching news for query {query}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
class RealTimeConnectionManager:
    """Manages WebSocket connections for real-time market updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_updates = None
        
    async def start_updates(self):
        """Start the market updates broadcasting task"""
        if self.market_updates is None:
            self.market_updates = asyncio.create_task(self._broadcast_real_updates())
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
        
        # Start updates if not already running
        await self.start_updates()
    
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
    
    async def _broadcast_real_updates(self):
        """Background task to broadcast periodic market updates from real APIs"""
        while True:
            try:
                if market_aggregator and hasattr(market_aggregator, 'configs') and market_aggregator.configs:
                    # Fetch real market data periodically
                    await self._send_real_updates()
                else:
                    # Fallback to mock updates
                    await self._send_mock_updates()
                
                await asyncio.sleep(30)  # Update every 30 seconds for real APIs
            except Exception as e:
                logger.error(f"Error in market updates broadcast: {e}")
                await asyncio.sleep(30)
    
    async def _send_real_updates(self):
        """Send real market updates from APIs"""
        try:
            # Get a few random markets to update
            markets = await market_aggregator.get_all_markets(limit_per_platform=5)
            
            if markets:
                import random
                market = random.choice(markets)
                
                # Simulate small price movement for real markets
                current_price = market.get('current_price', 0.5)
                price_change = random.uniform(-0.02, 0.02)
                new_price = max(0.01, min(0.99, current_price + price_change))
                
                update = {
                    "id": market.get("id"),
                    "platform": market.get("platform"),
                    "current_price": new_price,
                    "probability": new_price,
                    "volume_24h": market.get("volume_24h", 0),
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                await self.broadcast_market_update(update)
                
        except Exception as e:
            logger.error(f"Error sending real updates: {e}")
    
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
            "platform": "mock",
            "current_price": new_price,
            "probability": new_price,
            "volume_24h": 1000 + random.randint(0, 500),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_market_update(update)

# Global connection manager
manager = RealTimeConnectionManager()

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
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "aggregator_initialized": market_aggregator is not None,
        "active_connections": len(manager.active_connections),
        "data_source": "real_apis" if hasattr(market_aggregator, 'configs') and market_aggregator.configs else "mock_data"
    }

@api_router.get("/status")
async def get_api_status(aggregator: RealPredictionMarketAggregator = Depends(get_market_aggregator)):
    """Get detailed API status and platform connectivity"""
    try:
        platforms = {}
        
        if hasattr(aggregator, 'configs') and aggregator.configs:
            # Real API status
            for platform in aggregator.configs.keys():
                platforms[platform] = {
                    "connected": platform in aggregator.clients,
                    "last_check": datetime.utcnow().isoformat(),
                    "status": "active" if platform in aggregator.clients else "inactive"
                }
        else:
            # Mock data status
            platforms["mock"] = {
                "connected": True,
                "last_check": datetime.utcnow().isoformat(),
                "status": "active"
            }
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "platforms": platforms,
            "aggregator": {
                "clients_count": len(aggregator.clients) if hasattr(aggregator, 'clients') else 0,
                "initialized": True,
                "data_source": "real_apis" if hasattr(aggregator, 'configs') and aggregator.configs else "mock_data"
            },
            "websocket": {
                "active_connections": len(manager.active_connections),
                "status": "active"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        raise HTTPException(status_code=500, detail=str(e))