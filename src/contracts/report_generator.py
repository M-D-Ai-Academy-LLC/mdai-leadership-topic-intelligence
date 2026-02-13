"""Input/output contracts for the Report Generator agent."""

from typing import Dict, List, Optional

from pydantic import BaseModel

from models.competitors import Competitor
from models.keywords import Keyword, KeywordCluster
from models.reports import ReportConfig
from models.segments import IntentSegment
from models.topics import TopicCategory


class ReportInput(BaseModel):
    config: ReportConfig
    keywords: List[Keyword] = []
    clusters: List[KeywordCluster] = []
    topics: List[TopicCategory] = []
    segments: List[IntentSegment] = []
    gaps: List[TopicCategory] = []
    competitors: List[Competitor] = []


class ReportOutput(BaseModel):
    content: str
    format: str = "markdown"
    path: Optional[str] = None
    metadata: Dict = {}
