"""Intent segmentation and audience persona models."""

from typing import List, Optional

from pydantic import BaseModel


class IntentSegment(BaseModel):
    name: str
    description: str = ""
    query_intents: List[str] = []
    keywords: List[str] = []
    demand_signal: float = 0.0
    example_queries: List[str] = []


class AudiencePersona(BaseModel):
    name: str
    description: str = ""
    pain_points: List[str] = []
    goals: List[str] = []
    preferred_content_types: List[str] = []
    intent_segments: List[str] = []
