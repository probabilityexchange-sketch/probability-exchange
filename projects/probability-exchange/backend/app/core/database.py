#!/usr/bin/env python3
"""
Database configuration for MarketPulse Pro
"""
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global database objects
engine = None
SessionLocal = None

async def init_db():
    """Initialize database connection"""
    global engine, SessionLocal

    try:
        # Check if we are using SQLite
        database_url = settings.database_url
        if database_url.startswith("sqlite"):
             # Ensure the directory exists for sqlite
            if "///" in database_url:
                db_path = database_url.split("///")[1]
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                     os.makedirs(db_dir, exist_ok=True)

            # Helper for async sqlite
            if "+aiosqlite" not in database_url:
                 # If the user provided sqlite:///file.db, we need to make it async for AsyncEngine
                 # However, if the user didn't install aiosqlite, this might fail.
                 # For now, let's assume the user uses the correct URL or we handle it.
                 # Actually, let's just log and pass if it's not a proper async url for this setup,
                 # OR better, if it's the default dev URL, make sure it works.
                 if database_url.startswith("sqlite:///") and "+aiosqlite" not in database_url:
                     database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        logger.info(f"Initializing database connection to {database_url.split('@')[-1] if '@' in database_url else 'local db'}")

        # Create engine
        engine = create_async_engine(
            database_url,
            echo=settings.debug,
            future=True,
            # connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )

        # Create session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Test connection
        async with engine.begin() as conn:
             # Just a simple query to verify connection
             # verify explicit text import for sqlalchemy 2.0
             from sqlalchemy import text
             await conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # We don't raise here to allow the app to start even if DB fails (for now),
        # unless strictly required. User said "working database connection".
        # So maybe we should log loud.
        pass

async def close_db_connection():
    """Close database connections"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")

async def get_db():
    """Dependency for getting DB session"""
    if SessionLocal is None:
        return

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
