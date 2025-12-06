#!/usr/bin/env python3
"""
News API Endpoints

Provides news feed with AI sentiment analysis and market impact predictions
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from app.services.news_service import get_news_service, NewsService, NewsArticle

logger = logging.getLogger(__name__)

# Initialize router
news_router = APIRouter()


@news_router.get("/news")
async def get_news_feed(
    category: Optional[str] = None,
    limit: int = 20,
    news_service: NewsService = Depends(get_news_service)
):
    """
    Get news feed with AI sentiment analysis

    Query Parameters:
        category: Filter by category (crypto, politics, technology, economy, climate)
        limit: Maximum number of articles (default: 20)

    Returns:
        {
            "articles": [...],
            "total": int,
            "timestamp": str
        }
    """
    try:
        articles = await news_service.fetch_news(category=category, limit=limit)

        # Convert to dict for JSON response
        return {
            "articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "description": article.description,
                    "source": article.source,
                    "published_at": article.published_at.isoformat(),
                    "url": article.url,
                    "sentiment": {
                        "score": article.sentiment_score,
                        "label": article.sentiment_label
                    },
                    "impact": {
                        "score": article.impact_score,
                        "confidence": article.confidence,
                        "predicted_direction": article.predicted_direction
                    },
                    "related_markets": article.related_markets,
                    "category": article.category,
                    "is_breaking": article.is_breaking,
                    "signal_score": article.signal_score,
                    "impact_details": [
                        {
                            "market_name": d.market_name,
                            "platform": d.platform,
                            "start_prob": d.start_prob,
                            "end_prob": d.end_prob,
                            "interpretation": d.interpretation,
                            "market_url": d.market_url
                        }
                        for d in (article.impact_details or [])
                    ]
                }
                for article in articles
            ],
            "total": len(articles),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@news_router.get("/news/{article_id}")
async def get_news_article(
    article_id: str,
    news_service: NewsService = Depends(get_news_service)
):
    """Get detailed information for a specific news article"""
    try:
        articles = await news_service.fetch_news()

        for article in articles:
            if article.id == article_id:
                return {
                    "id": article.id,
                    "title": article.title,
                    "description": article.description,
                    "source": article.source,
                    "published_at": article.published_at.isoformat(),
                    "url": article.url,
                    "sentiment": {
                        "score": article.sentiment_score,
                        "label": article.sentiment_label
                    },
                    "impact": {
                        "score": article.impact_score,
                        "confidence": article.confidence,
                        "predicted_direction": article.predicted_direction
                    },
                    "related_markets": article.related_markets,
                    "category": article.category,
                    "is_breaking": article.is_breaking,
                    "signal_score": article.signal_score,
                    "impact_details": [
                        {
                            "market_name": d.market_name,
                            "platform": d.platform,
                            "start_prob": d.start_prob,
                            "end_prob": d.end_prob,
                            "interpretation": d.interpretation,
                            "market_url": d.market_url
                        }
                        for d in (article.impact_details or [])
                    ]
                }

        raise HTTPException(status_code=404, detail="Article not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@news_router.get("/news/impact/{market_id}")
async def get_market_news_impact(
    market_id: str,
    hours: int = 24,
    news_service: NewsService = Depends(get_news_service)
):
    """
    Get aggregated news impact analysis for a specific market

    Returns:
        {
            "market_id": str,
            "overall_sentiment": float (-1 to 1),
            "impact_score": float (0 to 1),
            "article_count": int,
            "predicted_direction": "up" | "down" | "neutral",
            "confidence": float (0 to 1),
            "key_articles": [...]
        }
    """
    try:
        impact = await news_service.get_market_impact(market_id, hours)
        return impact
    except Exception as e:
        logger.error(f"Error getting market impact for {market_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@news_router.get("/news/sentiment/summary")
async def get_sentiment_summary(
    news_service: NewsService = Depends(get_news_service)
):
    """
    Get overall sentiment summary across all news

    Returns:
        {
            "overall_sentiment": float,
            "positive_count": int,
            "negative_count": int,
            "neutral_count": int,
            "high_impact_count": int,
            "breaking_count": int
        }
    """
    try:
        articles = await news_service.fetch_news(limit=100)

        positive = sum(1 for a in articles if a.sentiment_label == 'positive')
        negative = sum(1 for a in articles if a.sentiment_label == 'negative')
        neutral = sum(1 for a in articles if a.sentiment_label == 'neutral')

        high_impact = sum(1 for a in articles if a.impact_score > 0.7)
        breaking = sum(1 for a in articles if a.is_breaking)

        avg_sentiment = sum(a.sentiment_score for a in articles) / len(articles) if articles else 0.0

        return {
            "overall_sentiment": avg_sentiment,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "high_impact_count": high_impact,
            "breaking_count": breaking,
            "total_articles": len(articles)
        }
    except Exception as e:
        logger.error(f"Error getting sentiment summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@news_router.get("/news/categories")
async def get_news_categories():
    """Get available news categories"""
    return {
        "categories": [
            {"id": "crypto", "name": "Cryptocurrency", "icon": "₿"},
            {"id": "politics", "name": "Politics", "icon": "🏛️"},
            {"id": "technology", "name": "Technology", "icon": "💻"},
            {"id": "economy", "name": "Economy", "icon": "📊"},
            {"id": "climate", "name": "Climate", "icon": "🌍"}
        ]
    }
