"""Input/output contracts for the Topic Clusterer agent."""

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from models.keywords import Keyword, KeywordCluster
from models.topics import TopicCategory


class TopicClusterInput(BaseModel):
    keywords: List[Keyword] = Field(..., min_length=1)
    n_clusters_range: Tuple[int, int] = (10, 30)
    method: str = "tfidf_kmeans"


class TopicClusterOutput(BaseModel):
    clusters: List[KeywordCluster] = []
    topics: List[TopicCategory] = []
    method_used: str = "tfidf_kmeans"
    metadata: Dict = {}
