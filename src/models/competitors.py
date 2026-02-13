"""Competitor analysis models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Competitor(BaseModel):
    domain: str
    name: Optional[str] = None
    content_count: int = 0
    top_topics: List[str] = []
    coverage_ratio: float = Field(default=0.0, ge=0, le=1)


class CompetitorContent(BaseModel):
    url: str
    title: str = ""
    topic: Optional[str] = None
    word_count: Optional[int] = None
    published_date: Optional[datetime] = None
