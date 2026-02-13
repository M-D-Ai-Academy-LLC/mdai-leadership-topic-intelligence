"""Topic category and trend models."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    BREAKOUT = "breakout"


class TopicCategory(BaseModel):
    name: str
    description: str = ""
    keywords: List[str] = []
    demand_signal: float = Field(default=0.0, ge=0, le=1)
    opportunity_score: float = Field(default=0.0, ge=0, le=1)
    gap_score: Optional[float] = Field(default=None, ge=0, le=1)


class TopicTrend(BaseModel):
    topic: str
    direction: TrendDirection
    momentum_score: float = 0.0
    period: str = "12m"
    data_points: List[Dict[str, Any]] = []
