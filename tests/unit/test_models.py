"""Unit tests for Pydantic data models."""

import pytest
from datetime import datetime


def test_keyword_with_volume():
    from models.keywords import Keyword
    kw = Keyword(term="leadership training", volume=5000, source="serpapi")
    assert kw.term == "leadership training"
    assert kw.volume == 5000


def test_keyword_without_volume():
    from models.keywords import Keyword
    kw = Keyword(term="leadership coaching", source="serpapi")
    assert kw.volume is None


def test_keyword_with_optional_fields():
    from models.keywords import Keyword, SearchIntent
    kw = Keyword(
        term="executive leadership",
        volume=12000,
        cpc=8.50,
        competition=0.75,
        search_intent=SearchIntent.INFORMATIONAL,
        trends_interest=72,
        trends_momentum=0.15,
        source="serpapi",
    )
    assert kw.competition == 0.75
    assert kw.search_intent == SearchIntent.INFORMATIONAL
    assert kw.trends_momentum == 0.15


def test_search_intent_enum():
    from models.keywords import SearchIntent
    assert SearchIntent.INFORMATIONAL.value == "informational"
    assert SearchIntent.TRANSACTIONAL.value == "transactional"
    assert SearchIntent.COMMERCIAL.value == "commercial"
    assert SearchIntent.NAVIGATIONAL.value == "navigational"


def test_keyword_cluster():
    from models.keywords import Keyword, KeywordCluster
    kw = Keyword(term="test", source="test")
    cluster = KeywordCluster(
        cluster_id=0,
        label="Test Cluster",
        keywords=[kw],
        size=1,
        avg_demand_signal=0.5,
    )
    assert cluster.size == 1
    assert cluster.avg_demand_signal == 0.5


def test_topic_category():
    from models.topics import TopicCategory
    topic = TopicCategory(
        name="Leadership Development",
        keywords=["leadership", "development"],
        demand_signal=0.75,
        opportunity_score=0.6,
    )
    assert topic.demand_signal == 0.75
    assert topic.gap_score is None


def test_topic_category_with_gap():
    from models.topics import TopicCategory
    topic = TopicCategory(
        name="Test",
        keywords=["test"],
        demand_signal=0.8,
        opportunity_score=0.7,
        gap_score=0.6,
    )
    assert topic.gap_score == 0.6


def test_trend_direction():
    from models.topics import TrendDirection, TopicTrend
    trend = TopicTrend(
        topic="AI Leadership",
        direction=TrendDirection.BREAKOUT,
        momentum_score=1.5,
    )
    assert trend.direction == TrendDirection.BREAKOUT


def test_intent_segment():
    from models.segments import IntentSegment
    segment = IntentSegment(
        name="Training",
        description="Training programs",
        keywords=["leadership training"],
        demand_signal=0.6,
    )
    assert segment.name == "Training"
    assert len(segment.keywords) == 1


def test_audience_persona():
    from models.segments import AudiencePersona
    persona = AudiencePersona(
        name="Corporate Learner",
        pain_points=["Finding quality programs"],
        goals=["Upskill workforce"],
    )
    assert persona.name == "Corporate Learner"


def test_competitor():
    from models.competitors import Competitor
    comp = Competitor(
        domain="hbr.org",
        name="HBR",
        content_count=100,
        coverage_ratio=0.8,
    )
    assert comp.coverage_ratio == 0.8


def test_report_config():
    from models.reports import ReportConfig
    config = ReportConfig(title="Test Report", query="leadership")
    assert config.output_format == "markdown"
    assert "executive_summary" in config.sections


def test_agent_response():
    from models.base import AgentResponse
    resp = AgentResponse(
        agent_name="test",
        task_id="abc123",
        status="success",
        data={"key": "value"},
    )
    assert resp.status == "success"
    assert resp.processing_time_seconds is None


def test_keyword_serialization():
    from models.keywords import Keyword
    kw = Keyword(term="test keyword", volume=1000, source="serpapi")
    data = kw.model_dump()
    assert data["term"] == "test keyword"
    assert data["volume"] == 1000
    # Round-trip
    kw2 = Keyword(**data)
    assert kw2.term == kw.term
    assert kw2.volume == kw.volume
