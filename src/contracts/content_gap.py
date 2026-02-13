"""Input/output contracts for the Content Gap agent."""

from typing import Dict, List

from pydantic import BaseModel, Field

from models.competitors import Competitor
from models.topics import TopicCategory


class ContentGapInput(BaseModel):
    topics: List[TopicCategory] = Field(..., min_length=1)
    competitors: List[Competitor] = Field(..., min_length=1)


class ContentGapOutput(BaseModel):
    gaps: List[TopicCategory] = []
    ranked_opportunities: List[Dict] = []
    metadata: Dict = {}
