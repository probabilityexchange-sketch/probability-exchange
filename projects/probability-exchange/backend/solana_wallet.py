#!/usr/bin/env python3
"""
Solana Wallet Integration for DFlow Trading

This module provides Solana wallet connectivity and transaction signing
for DFlow prediction market trading.

Supports:
- Phantom Wallet
- Solflare Wallet
- Ledger (via Solana adapter)
- Transaction signing and verification
"""

import base58
import base64
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

logger = logging.getLogger(__name__)


@dataclass
class SolanaWalletChallenge:
    """Challenge for Solana wallet authentication"""
    challenge: str
    wallet_address: str
    created_at: datetime
    expires_at: datetime
    nonce: str


class SolanaWalletManager:
    """
    Solana wallet manager for authentication and transaction signing

    Handles wallet connection, message signing verification, and session management
    for Solana wallets (Phantom, Solflare, etc.)
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.challenges: Dict[str, SolanaWalletChallenge] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def is_valid_solana_address(self, address: str) -> bool:
        """
        Validate Solana public key address format

        Args:
            address: Solana address to validate

        Returns:
            True if valid Solana address format
        """
        try:
            # Solana addresses are base58 encoded 32-byte public keys
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except Exception:
            return False

    def generate_challenge(
        self,
        wallet_address: str,
        expires_minutes: int = 15
    ) -> SolanaWalletChallenge:
        """
        Generate authentication challenge for Solana wallet

        Args:
            wallet_address: Solana wallet public key
            expires_minutes: Challenge expiration time in minutes

        Returns:
            SolanaWalletChallenge object
        """
        if not self.is_valid_solana_address(wallet_address):
            raise ValueError(f"Invalid Solana address: {wallet_address}")

        # Generate cryptographically secure nonce
        nonce = secrets.token_hex(16)

        # Create challenge message
        timestamp = datetime.utcnow()
        challenge_message = (
            f"Sign this message to authenticate with MarketPulse Pro\n\n"
            f"Wallet: {wallet_address}\n"
            f"Nonce: {nonce}\n"
            f"Timestamp: {timestamp.isoformat()}\n"
            f"Domain: marketpulsepro.com\n\n"
            f"This request will not trigger any blockchain transaction or cost any gas fees."
        )

        challenge = SolanaWalletChallenge(
            challenge=challenge_message,
            wallet_address=wallet_address,
            created_at=timestamp,
            expires_at=timestamp + timedelta(minutes=expires_minutes),
            nonce=nonce
        )

        # Store challenge
        self.challenges[nonce] = challenge

        return challenge

    def verify_signature(
        self,
        wallet_address: str,
        challenge_message: str,
        signature: str
    ) -> bool:
        """
        Verify Solana wallet signature

        Args:
            wallet_address: Solana wallet public key
            challenge_message: Original challenge message
            signature: Base58 or base64 encoded signature

        Returns:
            True if signature is valid
        """
        try:
            # Decode wallet address (public key)
            public_key_bytes = base58.b58decode(wallet_address)

            # Decode signature (try base58 first, then base64)
            try:
                signature_bytes = base58.b58decode(signature)
            except Exception:
                try:
                    signature_bytes = base64.b64decode(signature)
                except Exception as e:
                    logger.error(f"Failed to decode signature: {e}")
                    return False

            # Encode message to bytes
            message_bytes = challenge_message.encode('utf-8')

            # Verify signature using ed25519
            verify_key = VerifyKey(public_key_bytes)
            verify_key.verify(message_bytes, signature_bytes)

            logger.info(f"Successfully verified signature for {wallet_address}")
            return True

        except BadSignatureError:
            logger.warning(f"Invalid signature for {wallet_address}")
            return False
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    def create_session(
        self,
        wallet_address: str,
        expires_hours: int = 24
    ) -> str:
        """
        Create authenticated session for Solana wallet

        Args:
            wallet_address: Solana wallet public key
            expires_hours: Session expiration in hours

        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)

        session_data = {
            'wallet_address': wallet_address,
            'wallet_type': 'solana',
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=expires_hours),
            'is_active': True
        }

        self.sessions[session_id] = session_data

        logger.info(f"Created session {session_id} for Solana wallet {wallet_address}")
        return session_id

    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify and retrieve session data

        Args:
            session_id: Session identifier

        Returns:
            Session data if valid, None otherwise
        """
        session = self.sessions.get(session_id)

        if not session:
            return None

        # Check if expired
        if datetime.utcnow() > session['expires_at']:
            logger.info(f"Session {session_id} expired")
            del self.sessions[session_id]
            return None

        return session

    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session

        Args:
            session_id: Session identifier

        Returns:
            True if session was invalidated
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Invalidated session {session_id}")
            return True

        return False

    def get_active_sessions(self, wallet_address: str) -> list:
        """
        Get all active sessions for a wallet

        Args:
            wallet_address: Solana wallet address

        Returns:
            List of active session IDs
        """
        active_sessions = []

        for session_id, session_data in self.sessions.items():
            if (session_data['wallet_address'] == wallet_address and
                    datetime.utcnow() <= session_data['expires_at']):
                active_sessions.append(session_id)

        return active_sessions

    def cleanup_expired(self):
        """Remove expired challenges and sessions"""
        now = datetime.utcnow()

        # Remove expired challenges
        expired_challenges = [
            nonce for nonce, challenge in self.challenges.items()
            if now > challenge.expires_at
        ]
        for nonce in expired_challenges:
            del self.challenges[nonce]

        # Remove expired sessions
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if now > session['expires_at']
        ]
        for session_id in expired_sessions:
            del self.sessions[session_id]

        if expired_challenges or expired_sessions:
            logger.info(
                f"Cleaned up {len(expired_challenges)} challenges "
                f"and {len(expired_sessions)} sessions"
            )


class SolanaTransactionBuilder:
    """
    Helper class for building and preparing Solana transactions

    Provides utilities for creating transaction objects that can be signed
    by the user's wallet.
    """

    @staticmethod
    def prepare_swap_transaction(
        from_token: str,
        to_token: str,
        amount: str,
        user_public_key: str,
        dflow_instructions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare a swap transaction from DFlow instructions

        Args:
            from_token: Source token mint address
            to_token: Destination token mint address
            amount: Amount to swap
            user_public_key: User's Solana public key
            dflow_instructions: Instructions from DFlow API

        Returns:
            Transaction object ready for signing
        """
        return {
            'type': 'swap',
            'from_token': from_token,
            'to_token': to_token,
            'amount': amount,
            'user': user_public_key,
            'instructions': dflow_instructions.get('transaction'),
            'recent_blockhash': dflow_instructions.get('recentBlockhash'),
            'fee_payer': user_public_key
        }

    @staticmethod
    def prepare_market_order(
        market_id: str,
        outcome_token: str,
        amount: str,
        user_public_key: str,
        order_type: str = 'buy'
    ) -> Dict[str, Any]:
        """
        Prepare a prediction market order transaction

        Args:
            market_id: Prediction market identifier
            outcome_token: Token mint for desired outcome (YES/NO)
            amount: Amount to trade
            user_public_key: User's Solana public key
            order_type: 'buy' or 'sell'

        Returns:
            Transaction object for market order
        """
        return {
            'type': 'market_order',
            'market_id': market_id,
            'outcome_token': outcome_token,
            'amount': amount,
            'order_type': order_type,
            'user': user_public_key,
            'timestamp': datetime.utcnow().isoformat()
        }


# ============================================================================
# Testing
# ============================================================================

def test_solana_wallet():
    """Test Solana wallet functionality"""
    print("Testing Solana Wallet Manager...\n")

    manager = SolanaWalletManager(secret_key="test-secret-key")

    # Test address validation
    print("1. Testing address validation:")
    valid_address = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"  # Example Phantom wallet
    invalid_address = "not-a-valid-address"

    print(f"   Valid address: {manager.is_valid_solana_address(valid_address)}")
    print(f"   Invalid address: {manager.is_valid_solana_address(invalid_address)}")

    # Test challenge generation
    print("\n2. Testing challenge generation:")
    try:
        challenge = manager.generate_challenge(valid_address)
        print(f"   ✓ Challenge generated")
        print(f"   Nonce: {challenge.nonce}")
        print(f"   Expires: {challenge.expires_at}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # Test session creation
    print("\n3. Testing session management:")
    session_id = manager.create_session(valid_address)
    print(f"   ✓ Session created: {session_id[:16]}...")

    session_data = manager.verify_session(session_id)
    print(f"   ✓ Session verified: {session_data['wallet_address']}")

    print("\n✓ Solana Wallet Manager testing completed!")


if __name__ == "__main__":
    test_solana_wallet()
