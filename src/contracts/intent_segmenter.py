"""Input/output contracts for the Intent Segmenter agent."""

from typing import Dict, List

from pydantic import BaseModel, Field

from models.keywords import Keyword
from models.segments import AudiencePersona, IntentSegment


class IntentSegmentInput(BaseModel):
    keywords: List[Keyword] = Field(..., min_length=1)
    generate_personas: bool = True


class IntentSegmentOutput(BaseModel):
    segments: List[IntentSegment] = []
    personas: List[AudiencePersona] = []
    metadata: Dict = {}
