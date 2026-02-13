"""Base models and schemas for the topic intelligence system."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class DataSource(BaseModel):
    name: str
    url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reliability_score: float = Field(ge=0, le=1)


class AgentResponse(BaseModel):
    agent_name: str
    task_id: str
    status: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: Optional[float] = None
