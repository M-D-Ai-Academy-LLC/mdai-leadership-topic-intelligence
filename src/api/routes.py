"""API route handlers for the Leadership Topic Intelligence system."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.keyword_researcher import KeywordResearcherAgent
from agents.topic_clusterer import TopicClustererAgent
from agents.intent_segmenter import IntentSegmenterAgent
from agents.report_generator import ReportGeneratorAgent
from contracts.keyword_researcher import KeywordResearchInput
from contracts.topic_clusterer import TopicClusterInput
from contracts.intent_segmenter import IntentSegmentInput
from contracts.report_generator import ReportInput
from models.keywords import Keyword
from models.reports import ReportConfig

router = APIRouter()


class KeywordResearchRequest(BaseModel):
    queries: List[str]
    max_results: int = 100
    include_trends: bool = True


class TopicClusterRequest(BaseModel):
    keywords: List[dict]
    n_clusters_min: int = 10
    n_clusters_max: int = 30


class IntentSegmentRequest(BaseModel):
    keywords: List[dict]
    generate_personas: bool = True


class TrendsAnalyzeRequest(BaseModel):
    keywords: List[str]
    timeframe: str = "today 12-m"


class ReportGenerateRequest(BaseModel):
    query: str
    title: Optional[str] = None
    keywords: List[dict] = []


@router.post("/keywords/research")
async def research_keywords(request: KeywordResearchRequest):
    """Trigger keyword research."""
    agent = KeywordResearcherAgent()
    input_data = KeywordResearchInput(
        queries=request.queries,
        max_results=request.max_results,
        include_trends=request.include_trends,
    )
    result = await agent.process(input_data)
    return result.model_dump()


@router.post("/topics/cluster")
async def cluster_topics(request: TopicClusterRequest):
    """Trigger topic clustering."""
    agent = TopicClustererAgent()
    keywords = [Keyword(**kw) for kw in request.keywords]
    input_data = TopicClusterInput(
        keywords=keywords,
        n_clusters_range=(request.n_clusters_min, request.n_clusters_max),
    )
    result = await agent.process(input_data)
    return result.model_dump()


@router.post("/gaps/analyze")
async def analyze_gaps(request: dict):
    """Trigger content gap analysis."""
    return {"status": "not_implemented", "message": "Use the CLI for full gap analysis"}


@router.post("/trends/analyze")
async def analyze_trends(request: TrendsAnalyzeRequest):
    """Trigger trend analysis."""
    from integrations.google_trends_client import GoogleTrendsClient
    client = GoogleTrendsClient()
    interest = client.get_interest_over_time(request.keywords, request.timeframe)
    momentum = {}
    for kw in request.keywords:
        values = interest.get("interest_over_time", {}).get(kw, [])
        if values:
            momentum[kw] = client.calculate_momentum(values)
    return {"interest": interest, "momentum": momentum}


@router.post("/reports/generate")
async def generate_report(request: ReportGenerateRequest):
    """Generate a report."""
    agent = ReportGeneratorAgent()
    keywords = [Keyword(**kw) for kw in request.keywords]
    config = ReportConfig(
        title=request.title or f"Leadership Topic Intelligence: {request.query}",
        query=request.query,
    )
    input_data = ReportInput(config=config, keywords=keywords)
    result = await agent.process(input_data)
    return result.model_dump()
