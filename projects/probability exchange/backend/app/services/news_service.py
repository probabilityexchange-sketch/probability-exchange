#!/usr/bin/env python3
"""
News Service with AI Sentiment Analysis and Impact Predictions

Provides real-time news analysis, sentiment scoring, and market impact predictions
for prediction market trading intelligence.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import random
import re

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """News article with AI analysis"""
    id: str
    title: str
    description: str
    source: str
    published_at: datetime
    url: str
    sentiment_score: float  # -1.0 to 1.0
    sentiment_label: str  # positive, negative, neutral
    impact_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    predicted_direction: str  # up, down, neutral
    related_markets: List[str]
    category: str
    is_breaking: bool


class SentimentAnalyzer:
    """AI-powered sentiment analysis engine"""

    # Sentiment keywords with weights
    POSITIVE_KEYWORDS = {
        'surge': 0.8, 'soar': 0.8, 'rally': 0.7, 'boom': 0.8,
        'bull': 0.6, 'gains': 0.6, 'rises': 0.5, 'up': 0.4,
        'profit': 0.6, 'growth': 0.6, 'win': 0.7, 'success': 0.6,
        'breakthrough': 0.8, 'record': 0.7, 'high': 0.5
    }

    NEGATIVE_KEYWORDS = {
        'crash': -0.9, 'plunge': -0.8, 'collapse': -0.9, 'fall': -0.6,
        'bear': -0.6, 'losses': -0.7, 'drops': -0.6, 'down': -0.4,
        'crisis': -0.8, 'recession': -0.8, 'decline': -0.6, 'fail': -0.7,
        'risk': -0.5, 'concern': -0.4, 'low': -0.4
    }

    @classmethod
    def analyze(cls, text: str) -> tuple[float, str]:
        """
        Analyze text sentiment using keyword-based scoring

        Returns:
            (sentiment_score, sentiment_label)
            sentiment_score: -1.0 (very negative) to 1.0 (very positive)
            sentiment_label: 'positive', 'negative', or 'neutral'
        """
        text_lower = text.lower()
        score = 0.0
        word_count = 0

        # Check positive keywords
        for keyword, weight in cls.POSITIVE_KEYWORDS.items():
            if keyword in text_lower:
                score += weight
                word_count += 1

        # Check negative keywords
        for keyword, weight in cls.NEGATIVE_KEYWORDS.items():
            if keyword in text_lower:
                score += weight  # weight is already negative
                word_count += 1

        # Normalize score
        if word_count > 0:
            score = max(-1.0, min(1.0, score / max(word_count, 1)))

        # Determine label
        if score > 0.2:
            label = 'positive'
        elif score < -0.2:
            label = 'negative'
        else:
            label = 'neutral'

        return score, label


class MarketCorrelator:
    """Correlates news articles with prediction markets"""

    MARKET_KEYWORDS = {
        'crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain'],
        'politics': ['election', 'president', 'congress', 'senate', 'vote', 'political'],
        'technology': ['ai', 'artificial intelligence', 'tech', 'apple', 'google', 'microsoft'],
        'economy': ['fed', 'federal reserve', 'interest rate', 'inflation', 'gdp', 'economy'],
        'climate': ['climate', 'temperature', 'emissions', 'carbon', 'renewable']
    }

    @classmethod
    def find_related_markets(cls, title: str, description: str) -> tuple[List[str], str]:
        """
        Find related market categories based on content

        Returns:
            (related_categories, primary_category)
        """
        text = (title + ' ' + description).lower()
        related = []

        for category, keywords in cls.MARKET_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    related.append(category)
                    break

        primary = related[0] if related else 'general'
        return related, primary


class ImpactPredictor:
    """Predicts market impact from news"""

    @classmethod
    def predict_impact(
        cls,
        sentiment_score: float,
        source_credibility: float,
        recency_hours: float
    ) -> tuple[float, float, str]:
        """
        Predict market impact and confidence

        Returns:
            (impact_score, confidence, predicted_direction)
        """
        # Calculate base impact from sentiment
        base_impact = abs(sentiment_score)

        # Boost impact based on source credibility
        impact = base_impact * source_credibility

        # Recent news has higher impact
        recency_factor = max(0.5, 1.0 - (recency_hours / 24.0))
        impact *= recency_factor

        # Confidence increases with stronger sentiment and better sources
        confidence = (base_impact * 0.5 + source_credibility * 0.3 + recency_factor * 0.2)
        confidence = max(0.3, min(0.95, confidence))

        # Determine direction
        if sentiment_score > 0.2:
            direction = 'up'
        elif sentiment_score < -0.2:
            direction = 'down'
        else:
            direction = 'neutral'

        return impact, confidence, direction


class NewsService:
    """News aggregation and analysis service"""

    SOURCE_CREDIBILITY = {
        'Reuters': 0.95,
        'Bloomberg': 0.95,
        'Associated Press': 0.95,
        'Financial Times': 0.90,
        'Wall Street Journal': 0.90,
        'CNBC': 0.85,
        'CNN': 0.80,
        'BBC': 0.90,
        'The Guardian': 0.85,
        'CoinDesk': 0.80,
        'TechCrunch': 0.75
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _generate_mock_news(self) -> List[NewsArticle]:
        """Generate realistic mock news for demo"""
        mock_articles = [
            {
                'title': 'Bitcoin Surges Past $95,000 as Institutional Demand Soars',
                'description': 'Major investment firms increase crypto allocations as Bitcoin approaches six-figure milestone. Analysts predict continued momentum.',
                'source': 'Bloomberg',
                'category': 'crypto',
                'hours_ago': 1
            },
            {
                'title': 'Federal Reserve Signals Potential Rate Cut in Q2 2025',
                'description': 'Fed Chair hints at easing monetary policy as inflation shows signs of moderating. Markets react positively to dovish tone.',
                'source': 'Reuters',
                'category': 'economy',
                'hours_ago': 3
            },
            {
                'title': 'OpenAI Announces Major Breakthrough in AGI Research',
                'description': 'Company reveals new AI model with reasoning capabilities approaching human-level performance. Experts debate timeline to AGI.',
                'source': 'TechCrunch',
                'category': 'technology',
                'hours_ago': 5
            },
            {
                'title': '2024 Election Polls Show Tight Race in Key Swing States',
                'description': 'Latest polling data reveals narrow margins in Pennsylvania, Michigan, and Arizona. Analysts call it too close to call.',
                'source': 'Associated Press',
                'category': 'politics',
                'hours_ago': 2
            },
            {
                'title': 'Global Temperatures Set New Record High in 2024',
                'description': 'Climate scientists confirm 1.5°C warming threshold may be breached earlier than expected. Urgent action calls intensify.',
                'source': 'BBC',
                'category': 'climate',
                'hours_ago': 6
            },
            {
                'title': 'Ethereum Upgrade Promises 10x Speed Improvement',
                'description': 'Upcoming network upgrade expected to dramatically increase transaction throughput. Developer community optimistic.',
                'source': 'CoinDesk',
                'category': 'crypto',
                'hours_ago': 4
            },
            {
                'title': 'Major Tech Layoffs Announced Across Silicon Valley',
                'description': 'Leading technology companies announce workforce reductions citing economic uncertainty and AI automation.',
                'source': 'Wall Street Journal',
                'category': 'technology',
                'hours_ago': 8
            },
            {
                'title': 'Oil Prices Drop 15% on Demand Concerns',
                'description': 'Global oil markets see sharp decline as economic growth forecasts are revised downward. OPEC considers production cuts.',
                'source': 'Financial Times',
                'category': 'economy',
                'hours_ago': 12
            }
        ]

        articles = []
        for i, mock in enumerate(mock_articles):
            # Analyze sentiment
            full_text = mock['title'] + ' ' + mock['description']
            sentiment_score, sentiment_label = SentimentAnalyzer.analyze(full_text)

            # Find related markets
            related_markets, primary_category = MarketCorrelator.find_related_markets(
                mock['title'], mock['description']
            )

            # Get source credibility
            credibility = self.SOURCE_CREDIBILITY.get(mock['source'], 0.7)

            # Predict impact
            impact_score, confidence, direction = ImpactPredictor.predict_impact(
                sentiment_score, credibility, mock['hours_ago']
            )

            # Create article
            published_at = datetime.utcnow() - timedelta(hours=mock['hours_ago'])
            is_breaking = mock['hours_ago'] < 2

            article = NewsArticle(
                id=f"mock_{i}",
                title=mock['title'],
                description=mock['description'],
                source=mock['source'],
                published_at=published_at,
                url=f"https://example.com/news/{i}",
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                impact_score=impact_score,
                confidence=confidence,
                predicted_direction=direction,
                related_markets=related_markets,
                category=primary_category,
                is_breaking=is_breaking
            )
            articles.append(article)

        return articles

    async def fetch_news(
        self,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[NewsArticle]:
        """
        Fetch and analyze news articles

        Args:
            category: Optional category filter (crypto, politics, technology, etc.)
            limit: Maximum number of articles to return

        Returns:
            List of analyzed news articles
        """
        # For now, use mock data (NewsAPI integration can be added later)
        articles = self._generate_mock_news()

        # Filter by category if specified
        if category:
            articles = [a for a in articles if a.category == category]

        # Sort by recency (breaking news first)
        articles.sort(key=lambda x: (not x.is_breaking, x.published_at), reverse=True)

        return articles[:limit]

    async def get_market_impact(
        self,
        market_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get aggregated news impact for a specific market

        Returns impact analysis including:
        - Overall sentiment
        - Impact score
        - Key news articles
        - Predicted direction
        """
        articles = await self.fetch_news()

        # Filter articles relevant to this market (simplified for mock)
        relevant = [a for a in articles if a.impact_score > 0.5]

        if not relevant:
            return {
                'market_id': market_id,
                'overall_sentiment': 0.0,
                'impact_score': 0.0,
                'article_count': 0,
                'predicted_direction': 'neutral',
                'confidence': 0.0,
                'key_articles': []
            }

        # Calculate aggregate metrics
        avg_sentiment = sum(a.sentiment_score for a in relevant) / len(relevant)
        max_impact = max(a.impact_score for a in relevant)
        avg_confidence = sum(a.confidence for a in relevant) / len(relevant)

        # Determine overall direction
        if avg_sentiment > 0.2:
            direction = 'up'
        elif avg_sentiment < -0.2:
            direction = 'down'
        else:
            direction = 'neutral'

        return {
            'market_id': market_id,
            'overall_sentiment': avg_sentiment,
            'impact_score': max_impact,
            'article_count': len(relevant),
            'predicted_direction': direction,
            'confidence': avg_confidence,
            'key_articles': [
                {
                    'title': a.title,
                    'source': a.source,
                    'sentiment': a.sentiment_label,
                    'impact': a.impact_score,
                    'url': a.url
                }
                for a in relevant[:5]
            ]
        }


# Global service instance
_news_service: Optional[NewsService] = None


async def get_news_service() -> NewsService:
    """Get or create news service instance"""
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
        await _news_service.__aenter__()
    return _news_service
