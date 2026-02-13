"""API route handlers for the Leadership Topic Intelligence system."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from agents.content_gap import ContentGapAgent
from agents.keyword_researcher import KeywordResearcherAgent
from agents.topic_clusterer import TopicClustererAgent
from agents.intent_segmenter import IntentSegmenterAgent
from agents.report_generator import ReportGeneratorAgent
from contracts.content_gap import ContentGapInput
from contracts.keyword_researcher import KeywordResearchInput
from contracts.topic_clusterer import TopicClusterInput
from contracts.intent_segmenter import IntentSegmentInput
from contracts.report_generator import ReportInput
from models.competitors import Competitor
from models.keywords import Keyword
from models.reports import ReportConfig
from models.topics import TopicCategory

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


class ContentGapAnalyzeRequest(BaseModel):
    topics: List[dict]
    competitors: List[dict]


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
async def analyze_gaps(request: ContentGapAnalyzeRequest):
    """Trigger content gap analysis."""
    if not request.topics:
        raise HTTPException(status_code=422, detail="topics must contain at least one item")
    if not request.competitors:
        raise HTTPException(status_code=422, detail="competitors must contain at least one item")

    agent = ContentGapAgent()
    try:
        topics = [TopicCategory(**topic) for topic in request.topics]
        competitors = [Competitor(**competitor) for competitor in request.competitors]
        input_data = ContentGapInput(topics=topics, competitors=competitors)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()) from e

    result = await agent.process(input_data)
    return result.model_dump()


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
