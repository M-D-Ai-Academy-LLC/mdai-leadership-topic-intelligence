"""Report configuration and section models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ReportConfig(BaseModel):
    title: str
    query: str
    report_type: str = "full"
    sections: List[str] = [
        "executive_summary",
        "top_keywords",
        "topic_clusters",
        "intent_segments",
        "opportunity_scores",
        "momentum_trends",
    ]
    output_format: str = "markdown"


class ReportSection(BaseModel):
    title: str
    content: str = ""
    data: Dict[str, Any] = {}
    order: int = 0
