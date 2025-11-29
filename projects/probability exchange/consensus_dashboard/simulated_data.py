#!/usr/bin/env python3
"""
Simulated data utilities for the Probex Consensus Dashboard MVP
This module removes external dependencies and provides in-memory demo data
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random

CATEGORIES = ["politics", "economy", "technology", "sports", "entertainment", "health"]
PLATFORMS = ["Polymarket", "Kalshi", "Manifold"]


def _rand_prob_pair() -> Tuple[float, float]:
    p = random.uniform(0.2, 0.9)
    return round(p, 3), round(1 - p, 3)


def _rand_category() -> str:
    return random.choice(CATEGORIES)


@dataclass
class SimulatedSignal:
    question: str
    category: str
    market_consensus: Dict[str, float]
    cross_platform_consensus: float
    confidence_score: float
    prediction_strength: str
    risk_adjusted_return: float
    volume_weighted_score: float


class SimulatedDataManager:
    """Generates consistent simulated markets and signals for the dashboard"""

    def __init__(self, seed: int | None = 42):
        self.random = random.Random(seed)

    def generate_markets(self, n: int = 50) -> List[Dict]:
        markets = []
        for i in range(n):
            p_yes, p_no = _rand_prob_pair()
            platform = self.random.choice(PLATFORMS)
            markets.append(
                {
                    "id": f"mkt_{i}",
                    "question": f"Will event {i} occur by {datetime.now().year}?",
                    "category": _rand_category(),
                    "outcomes": ["Yes", "No"],
                    "probabilities": [p_yes, p_no],
                    "volume": int(self.random.uniform(1_000, 200_000)),
                    "liquidity": int(self.random.uniform(5_000, 100_000)),
                    "open_time": datetime.now() - timedelta(days=self.random.randint(0, 30)),
                    "close_time": datetime.now() + timedelta(days=self.random.randint(5, 60)),
                    "url": "https://example.com",
                    "status": "open",
                    "source": platform,
                }
            )
        return markets

    def compute_signals(self, markets: List[Dict]) -> List[Dict]:
        signals: List[Dict] = []
        # Group by pseudo-question family (chunk by 3)
        for i in range(0, max(1, len(markets) - 2), 3):
            group = markets[i : i + 3]
            if not group:
                continue
            category = group[0]["category"]

            # Average probabilities across platforms (use Yes prob if available)
            probs = []
            platform_breakdown = {}
            total_volume = 0
            vol_score = 0.0
            for m in group:
                p_yes = m.get("probabilities", [0.5, 0.5])[0]
                probs.append(p_yes)
                platform = m.get("source", "Unknown")
                platform_breakdown[platform] = p_yes
                v = float(m.get("volume", 0))
                total_volume += v
                vol_score += p_yes * (v ** 0.5)

            consensus = sum(probs) / len(probs)
            confidence = min(0.95, 0.55 + 0.4 * abs(consensus - 0.5) + 0.05 * (len(group) - 1))

            if consensus >= 0.8:
                strength = "strong"
            elif consensus >= 0.65:
                strength = "moderate"
            else:
                strength = "weak"

            risk_adj = (consensus - 0.5) * 0.6
            vol_weighted = vol_score / max(1.0, total_volume ** 0.5)

            signals.append(
                {
                    "question": f"Consensus for {category} trend {i//3}",
                    "category": category,
                    "market_consensus": platform_breakdown,
                    "cross_platform_consensus": round(consensus, 3),
                    "confidence_score": round(confidence, 3),
                    "prediction_strength": strength,
                    "risk_adjusted_return": round(max(0.0, risk_adj), 3),
                    "volume_weighted_score": round(vol_weighted, 3),
                }
            )
        return signals


def generate_sample_signals(n_markets: int = 60) -> List[Dict]:
    mgr = SimulatedDataManager()
    mkts = mgr.generate_markets(n_markets)
    return mgr.compute_signals(mkts)
