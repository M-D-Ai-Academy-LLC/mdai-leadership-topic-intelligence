"""Keyword and search data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchIntent(str, Enum):
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


class Keyword(BaseModel):
    term: str
    volume: Optional[int] = None
    cpc: Optional[float] = None
    competition: Optional[float] = Field(default=None, ge=0, le=1)
    search_intent: Optional[SearchIntent] = None
    related_queries: List[str] = []
    people_also_ask: List[str] = []
    serp_features: List[str] = []
    trends_interest: Optional[int] = Field(default=None, ge=0, le=100)
    trends_momentum: Optional[float] = None
    source: str = "serpapi"


class KeywordCluster(BaseModel):
    cluster_id: int
    label: str
    keywords: List[Keyword] = []
    size: int = 0
    avg_demand_signal: float = 0.0
    top_intent: Optional[SearchIntent] = None


class SearchVolumeTimeSeries(BaseModel):
    keyword: str
    timestamps: List[datetime] = []
    values: List[int] = []
    source: str = "trends"
