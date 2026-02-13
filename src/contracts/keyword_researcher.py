"""Input/output contracts for the Keyword Researcher agent."""

from typing import Dict, List

from pydantic import BaseModel, Field

from models.keywords import Keyword, KeywordCluster


class KeywordResearchInput(BaseModel):
    queries: List[str] = Field(..., min_length=1)
    max_results: int = Field(default=100, ge=1, le=1000)
    include_trends: bool = True
    include_paa: bool = True


class KeywordResearchOutput(BaseModel):
    keywords: List[Keyword] = []
    clusters: List[KeywordCluster] = []
    total_discovered: int = 0
    metadata: Dict = {}
