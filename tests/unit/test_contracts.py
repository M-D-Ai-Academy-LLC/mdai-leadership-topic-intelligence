"""Unit tests for agent I/O contracts."""

import pytest


def test_keyword_research_input_valid():
    from contracts.keyword_researcher import KeywordResearchInput
    inp = KeywordResearchInput(queries=["leadership training"])
    assert len(inp.queries) == 1
    assert inp.max_results == 100


def test_keyword_research_input_empty_queries():
    from contracts.keyword_researcher import KeywordResearchInput
    with pytest.raises(Exception):
        KeywordResearchInput(queries=[])


def test_keyword_research_output():
    from contracts.keyword_researcher import KeywordResearchOutput
    from models.keywords import Keyword
    kw = Keyword(term="test", source="test")
    out = KeywordResearchOutput(keywords=[kw], total_discovered=1)
    assert out.total_discovered == 1


def test_topic_cluster_input():
    from contracts.topic_clusterer import TopicClusterInput
    from models.keywords import Keyword
    kw = Keyword(term="test", source="test")
    inp = TopicClusterInput(keywords=[kw])
    assert inp.method == "tfidf_kmeans"
    assert inp.n_clusters_range == (10, 30)


def test_topic_cluster_output():
    from contracts.topic_clusterer import TopicClusterOutput
    out = TopicClusterOutput(clusters=[], topics=[], method_used="tfidf_kmeans")
    assert out.method_used == "tfidf_kmeans"


def test_intent_segment_input():
    from contracts.intent_segmenter import IntentSegmentInput
    from models.keywords import Keyword
    kw = Keyword(term="leadership coaching", source="test")
    inp = IntentSegmentInput(keywords=[kw])
    assert inp.generate_personas is True


def test_intent_segment_output():
    from contracts.intent_segmenter import IntentSegmentOutput
    out = IntentSegmentOutput(segments=[], personas=[])
    assert len(out.segments) == 0


def test_content_gap_input():
    from contracts.content_gap import ContentGapInput
    from models.topics import TopicCategory
    from models.competitors import Competitor
    topic = TopicCategory(name="Test", keywords=["test"])
    comp = Competitor(domain="test.com")
    inp = ContentGapInput(topics=[topic], competitors=[comp])
    assert len(inp.topics) == 1


def test_content_gap_output():
    from contracts.content_gap import ContentGapOutput
    out = ContentGapOutput(gaps=[], ranked_opportunities=[])
    assert len(out.gaps) == 0


def test_report_input():
    from contracts.report_generator import ReportInput
    from models.reports import ReportConfig
    config = ReportConfig(title="Test", query="test")
    inp = ReportInput(config=config)
    assert len(inp.keywords) == 0


def test_report_output():
    from contracts.report_generator import ReportOutput
    out = ReportOutput(content="# Report", format="markdown")
    assert out.path is None
