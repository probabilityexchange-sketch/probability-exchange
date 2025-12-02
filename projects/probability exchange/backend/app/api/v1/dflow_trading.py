#!/usr/bin/env python3
"""
DFlow Solana Trading API Router

This module provides API endpoints for DFlow/Solana prediction market trading:
- Solana wallet authentication
- Market discovery and quotes
- Token swaps (imperative and declarative modes)
- Position tracking
- Transaction management

Integrates with DFlow pond.dflow.net API for tokenized Kalshi markets on Solana.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import logging
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from dflow_client import DFlowAPIClient, DFlowConfig, create_dflow_config
from solana_wallet import SolanaWalletManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API router
dflow_router = APIRouter()

# Global instances
dflow_client: Optional[DFlowAPIClient] = None
solana_wallet_manager: Optional[SolanaWalletManager] = None


# ============================================================================
# Pydantic Models
# ============================================================================

class SolanaAuthChallenge(BaseModel):
    wallet_address: str = Field(..., description="Solana wallet public key")


class SolanaAuthVerify(BaseModel):
    wallet_address: str = Field(..., description="Solana wallet public key")
    challenge: str = Field(..., description="Challenge message that was signed")
    signature: str = Field(..., description="Base58 or base64 encoded signature")


class SwapQuoteRequest(BaseModel):
    input_token: str = Field(..., description="Input token mint address")
    output_token: str = Field(..., description="Output token mint address")
    amount: str = Field(..., description="Amount of input token")
    slippage_tolerance: float = Field(0.01, description="Maximum slippage (0.01 = 1%)")


class SwapExecuteRequest(BaseModel):
    input_token: str = Field(..., description="Input token mint address")
    output_token: str = Field(..., description="Output token mint address")
    amount: str = Field(..., description="Amount of input token")
    wallet_address: str = Field(..., description="User's Solana wallet address")
    session_id: str = Field(..., description="Authenticated session ID")
    mode: str = Field("declarative", description="Swap mode: 'imperative' or 'declarative'")
    slippage_tolerance: float = Field(0.01, description="Maximum slippage")
    priority_fee: Optional[int] = Field(None, description="Optional priority fee in lamports")


# ============================================================================
# Dependency Injection
# ============================================================================

async def get_dflow_client() -> DFlowAPIClient:
    """Dependency to get DFlow API client"""
    global dflow_client
    if dflow_client is None:
        await initialize_dflow_client()
    return dflow_client


async def get_solana_wallet_manager() -> SolanaWalletManager:
    """Dependency to get Solana wallet manager"""
    global solana_wallet_manager
    if solana_wallet_manager is None:
        await initialize_solana_wallet_manager()
    return solana_wallet_manager


async def initialize_dflow_client():
    """Initialize DFlow API client"""
    global dflow_client
    if dflow_client is not None:
        return

    logger.info("Initializing DFlow API Client...")

    config = create_dflow_config()
    dflow_client = DFlowAPIClient(config)

    logger.info("DFlow API Client initialized")


async def initialize_solana_wallet_manager():
    """Initialize Solana wallet manager"""
    global solana_wallet_manager
    if solana_wallet_manager is not None:
        return

    logger.info("Initializing Solana Wallet Manager...")

    secret_key = os.getenv('SOLANA_WALLET_SECRET_KEY', 'default-secret-key-for-demo')
    solana_wallet_manager = SolanaWalletManager(secret_key)

    logger.info("Solana Wallet Manager initialized")


# ============================================================================
# Authentication Endpoints
# ============================================================================

@dflow_router.post("/auth/solana/challenge")
async def create_solana_auth_challenge(
    request: SolanaAuthChallenge,
    wallet_manager: SolanaWalletManager = Depends(get_solana_wallet_manager)
):
    """
    Create authentication challenge for Solana wallet

    The user must sign this challenge message with their wallet to authenticate.
    """
    try:
        if not wallet_manager.is_valid_solana_address(request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid Solana wallet address")

        challenge = wallet_manager.generate_challenge(request.wallet_address)

        return {
            "challenge": challenge.challenge,
            "nonce": challenge.nonce,
            "expires_at": challenge.expires_at.isoformat(),
            "wallet_address": request.wallet_address
        }

    except Exception as e:
        logger.error(f"Failed to create Solana auth challenge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dflow_router.post("/auth/solana/verify")
async def verify_solana_auth_signature(
    request: SolanaAuthVerify,
    wallet_manager: SolanaWalletManager = Depends(get_solana_wallet_manager)
):
    """
    Verify Solana wallet signature and create authenticated session

    After verification, the session ID can be used for trading operations.
    """
    try:
        # Verify signature
        is_valid = wallet_manager.verify_signature(
            request.wallet_address,
            request.challenge,
            request.signature
        )

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Create session
        session_id = wallet_manager.create_session(request.wallet_address)

        return {
            "success": True,
            "session_id": session_id,
            "wallet_address": request.wallet_address,
            "wallet_type": "solana",
            "expires_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify Solana signature: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Market Discovery Endpoints
# ============================================================================

@dflow_router.get("/markets")
async def get_dflow_markets(
    category: Optional[str] = None,
    limit: int = 100,
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """
    Get available tokenized prediction markets from DFlow

    These are Kalshi markets available as SPL tokens on Solana.
    """
    try:
        async with client:
            markets = await client.get_prediction_markets(category, limit)

        return {
            "markets": markets,
            "total": len(markets),
            "platform": "dflow",
            "chain": "solana",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to fetch DFlow markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dflow_router.get("/markets/{market_id}")
async def get_dflow_market_detail(
    market_id: str,
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """Get detailed information about a specific DFlow prediction market"""
    try:
        async with client:
            market = await client.get_market_detail(market_id)

        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        return {
            "market": market,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch DFlow market {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Trading Endpoints
# ============================================================================

@dflow_router.post("/trading/quote")
async def get_swap_quote(
    request: SwapQuoteRequest,
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """
    Get a swap quote for trading prediction market tokens

    Example: Get quote for swapping USDC to YES token on a market
    """
    try:
        async with client:
            quote = await client.get_swap_quote(
                input_token=request.input_token,
                output_token=request.output_token,
                amount=request.amount,
                slippage_tolerance=request.slippage_tolerance
            )

        if not quote:
            raise HTTPException(status_code=400, detail="Failed to get swap quote")

        return {
            "quote": {
                "in_token": quote.in_token,
                "out_token": quote.out_token,
                "in_amount": quote.in_amount,
                "out_amount": quote.out_amount,
                "price_impact": quote.price_impact,
                "estimated_slippage": quote.estimated_slippage,
                "route": quote.route,
                "expires_at": quote.expires_at.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get swap quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dflow_router.post("/trading/swap")
async def execute_swap(
    request: SwapExecuteRequest,
    client: DFlowAPIClient = Depends(get_dflow_client),
    wallet_manager: SolanaWalletManager = Depends(get_solana_wallet_manager)
):
    """
    Execute a token swap transaction

    Supports two modes:
    - imperative: Full control over transaction (review before signing)
    - declarative: Lightweight multi-transaction with reduced slippage

    Returns transaction data that must be signed by the user's wallet.
    """
    try:
        # Verify session
        session = wallet_manager.verify_session(request.session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        if session['wallet_address'] != request.wallet_address:
            raise HTTPException(status_code=403, detail="Wallet address mismatch")

        async with client:
            if request.mode == "imperative":
                # First get quote
                quote = await client.get_swap_quote(
                    input_token=request.input_token,
                    output_token=request.output_token,
                    amount=request.amount,
                    slippage_tolerance=request.slippage_tolerance
                )

                if not quote:
                    raise HTTPException(status_code=400, detail="Failed to get swap quote")

                # Execute imperative swap
                result = await client.execute_swap_imperative(
                    quote=quote,
                    user_public_key=request.wallet_address,
                    priority_fee=request.priority_fee
                )

            else:  # declarative mode
                # Execute declarative swap
                result = await client.execute_swap_declarative(
                    input_token=request.input_token,
                    output_token=request.output_token,
                    amount=request.amount,
                    user_public_key=request.wallet_address,
                    slippage_tolerance=request.slippage_tolerance
                )

        return {
            "success": True,
            "mode": request.mode,
            "result": result,
            "wallet_address": request.wallet_address,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dflow_router.get("/trading/order/{order_id}")
async def get_order_status(
    order_id: str,
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """Get status of a swap order"""
    try:
        async with client:
            status = await client.get_order_status(order_id)

        return {
            "order": status,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get order status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Portfolio Endpoints
# ============================================================================

@dflow_router.get("/portfolio/positions/{wallet_address}")
async def get_user_positions(
    wallet_address: str,
    session_id: str,
    client: DFlowAPIClient = Depends(get_dflow_client),
    wallet_manager: SolanaWalletManager = Depends(get_solana_wallet_manager)
):
    """Get user's prediction market positions on Solana"""
    try:
        # Verify session
        session = wallet_manager.verify_session(session_id)
        if not session or session['wallet_address'] != wallet_address:
            raise HTTPException(status_code=401, detail="Unauthorized")

        async with client:
            positions = await client.get_user_positions(wallet_address)

        return {
            "wallet_address": wallet_address,
            "positions": [
                {
                    "market_id": pos.market_id,
                    "token_mint": pos.token_mint,
                    "outcome": pos.outcome,
                    "shares": str(pos.shares),
                    "average_price": str(pos.average_price),
                    "current_value": str(pos.current_value),
                    "pnl": str(pos.pnl),
                    "platform": pos.platform
                }
                for pos in positions
            ],
            "total": len(positions),
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dflow_router.get("/portfolio/balance/{wallet_address}")
async def get_wallet_balance(
    wallet_address: str,
    session_id: str,
    token_mint: Optional[str] = None,
    client: DFlowAPIClient = Depends(get_dflow_client),
    wallet_manager: SolanaWalletManager = Depends(get_solana_wallet_manager)
):
    """Get Solana wallet token balances"""
    try:
        # Verify session
        session = wallet_manager.verify_session(session_id)
        if not session or session['wallet_address'] != wallet_address:
            raise HTTPException(status_code=401, detail="Unauthorized")

        async with client:
            balance = await client.get_wallet_balance(wallet_address, token_mint)

        return {
            "wallet_address": wallet_address,
            "balance": balance,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get wallet balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Token & Venue Information
# ============================================================================

@dflow_router.get("/tokens")
async def get_available_tokens(
    include_decimals: bool = True,
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """Get list of available tokens for trading"""
    try:
        async with client:
            tokens = await client.get_available_tokens(include_decimals)

        return {
            "tokens": tokens,
            "total": len(tokens),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get available tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dflow_router.get("/venues")
async def get_trading_venues(
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """Get list of liquidity venues"""
    try:
        async with client:
            venues = await client.get_trading_venues()

        return {
            "venues": venues,
            "total": len(venues),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get trading venues: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@dflow_router.get("/health")
async def dflow_health_check(
    client: DFlowAPIClient = Depends(get_dflow_client)
):
    """DFlow trading service health check"""
    try:
        async with client:
            is_healthy = await client.health_check()

        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": "dflow-trading",
            "chain": "solana",
            "version": "1.0.0",
            "api_accessible": is_healthy,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"DFlow health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "dflow-trading",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
