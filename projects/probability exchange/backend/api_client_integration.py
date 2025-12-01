#!/usr/bin/env python3
"""
FastAPI Client Integration for MarketPulse Pro Dashboard

This module provides the connection between the React dashboard and the FastAPI backend,
including WebSocket support for real-time market data updates.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
import websockets
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for api_clients import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_clients import PredictionMarketAggregator, MarketData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastAPIClient:
    """Client for interacting with the FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = None
        self.websocket = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()
    
    async def get_markets(self, category: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get aggregated markets from the API"""
        try:
            params = {"limit": limit}
            if category:
                params["category"] = category
                
            async with self.session.get(f"{self.api_base}/markets", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch markets: {response.status}")
                    return {"markets": [], "total": 0, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return {"markets": [], "total": 0, "error": str(e)}
    
    async def get_market_details(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific market"""
        try:
            async with self.session.get(f"{self.api_base}/markets/{market_id}") as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.warning(f"Market {market_id} not found")
                    return None
                else:
                    logger.error(f"Failed to fetch market {market_id}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    async def compare_markets(self, question: str) -> Dict[str, Any]:
        """Compare markets across platforms"""
        try:
            params = {"question": question}
            async with self.session.get(f"{self.api_base}/markets/compare", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to compare markets: {response.status}")
                    return {"question": question, "platforms": {}, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error comparing markets: {e}")
            return {"question": question, "platforms": {}, "error": str(e)}
    
    async def get_api_status(self) -> Dict[str, Any]:
        """Get API status information"""
        try:
            async with self.session.get(f"{self.api_base}/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get API status: {response.status}")
                    return {"status": "error", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error getting API status: {e}")
            return {"status": "error", "error": str(e)}

class WebSocketMarketClient:
    """WebSocket client for real-time market updates"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.websocket = None
        self.callbacks = []
        
    async def connect(self):
        """Connect to the WebSocket endpoint"""
        try:
            websocket_url = f"{self.base_url}/api/v1/ws/markets"
            logger.info(f"Connecting to WebSocket: {websocket_url}")
            
            self.websocket = await websockets.connect(websocket_url)
            logger.info("WebSocket connection established")
            
            # Start listening for messages
            asyncio.create_task(self._listen_for_messages())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            return False
    
    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in WebSocket message listener: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get("type")
        
        if message_type == "market_update":
            # Broadcast to all callbacks
            for callback in self.callbacks:
                try:
                    await callback(data.get("data"))
                except Exception as e:
                    logger.error(f"Error in market update callback: {e}")
        
        elif message_type == "ack":
            # Keepalive acknowledgment
            logger.debug("WebSocket keepalive acknowledged")
        
        else:
            logger.debug(f"Received WebSocket message: {data}")
    
    async def send_message(self, message: Dict[str, Any]):
        """Send a message through WebSocket"""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send WebSocket message: {e}")
    
    def add_callback(self, callback):
        """Add a callback function for market updates"""
        self.callbacks.append(callback)
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

class MarketDataCache:
    """Simple cache for market data to improve performance"""
    
    def __init__(self, ttl_seconds: int = 30):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any):
        """Cache data with current timestamp"""
        self.cache[key] = (data, datetime.now())
    
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()

class DashboardIntegration:
    """Main integration class for connecting dashboard to FastAPI backend"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.api_client = None
        self.websocket_client = None
        self.cache = MarketDataCache()
        self.subscribed_markets = set()
        
    async def initialize(self):
        """Initialize the integration"""
        try:
            # Initialize API client
            self.api_client = FastAPIClient(self.api_base_url)
            await self.api_client.__aenter__()
            
            # Initialize WebSocket client
            self.websocket_client = WebSocketMarketClient(self.api_base_url)
            connected = await self.websocket_client.connect()
            
            if connected:
                # Add market update callback
                self.websocket_client.add_callback(self._on_market_update)
            
            logger.info("Dashboard integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard integration: {e}")
            return False
    
    async def _on_market_update(self, market_data: Dict[str, Any]):
        """Handle real-time market updates"""
        market_id = market_data.get("id")
        if market_id:
            # Cache the update
            self.cache.set(f"market_{market_id}", market_data)
            self.subscribed_markets.add(market_id)
            
            # Log the update
            price = market_data.get("current_price", "N/A")
            platform = market_data.get("platform", "unknown")
            logger.info(f"Market update: {market_id} on {platform} - Price: {price}")
    
    async def get_cached_markets(self, category: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get markets with caching"""
        cache_key = f"markets_{category}_{limit}"
        
        # Try to get from cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug("Returning cached market data")
            return cached_data
        
        # Fetch from API
        if self.api_client:
            data = await self.api_client.get_markets(category, limit)
            # Cache the result
            self.cache.set(cache_key, data)
            return data
        
        return {"markets": [], "total": 0, "error": "API client not initialized"}
    
    async def get_cached_market_details(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market details with caching"""
        cache_key = f"market_detail_{market_id}"
        
        # Try to get from cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached market details for {market_id}")
            return cached_data
        
        # Fetch from API
        if self.api_client:
            data = await self.api_client.get_market_details(market_id)
            if data:
                # Cache the result
                self.cache.set(cache_key, data)
            return data
        
        return None
    
    async def compare_markets(self, question: str) -> Dict[str, Any]:
        """Compare markets across platforms"""
        if self.api_client:
            return await self.api_client.compare_markets(question)
        return {"question": question, "platforms": {}, "error": "API client not initialized"}
    
    async def get_real_time_update(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest real-time update for a market"""
        cache_key = f"market_{market_id}"
        return self.cache.get(cache_key)
    
    async def get_api_status(self) -> Dict[str, Any]:
        """Get API status"""
        if self.api_client:
            return await self.api_client.get_api_status()
        return {"status": "error", "error": "API client not initialized"}
    
    async def cleanup(self):
        """Clean up resources"""
        if self.api_client:
            await self.api_client.__aexit__(None, None, None)
        
        if self.websocket_client:
            await self.websocket_client.disconnect()
        
        self.cache.clear()
        logger.info("Dashboard integration cleaned up")

# Demo function to test the integration
async def test_dashboard_integration():
    """Test the dashboard integration"""
    print("Testing Dashboard Integration...")
    
    # Note: This would require the FastAPI backend to be running
    integration = DashboardIntegration()
    
    try:
        # Initialize (will fail if backend not running)
        # initialized = await integration.initialize()
        # if initialized:
        #     # Test market data fetching
        #     markets_data = await integration.get_cached_markets(category="crypto", limit=10)
        #     print(f"Fetched {markets_data.get('total', 0)} markets")
        #     
        #     # Test API status
        #     status = await integration.get_api_status()
        #     print(f"API Status: {status}")
        
        print("Dashboard integration framework ready!")
        
    except Exception as e:
        print(f"Integration test error: {e}")
    finally:
        await integration.cleanup()

if __name__ == "__main__":
    asyncio.run(test_dashboard_integration())