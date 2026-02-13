"""Shared test fixtures for the topic intelligence test suite."""

import os
import sys
from pathlib import Path

import pytest

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Force no-network mode for all tests
os.environ["NO_NETWORK_MODE"] = "true"
os.environ["ENABLE_SERPAPI"] = "true"
os.environ["ENABLE_TRENDS"] = "true"
os.environ["ENABLE_COMPETITORS"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./data/test_topic_intel.db"


@pytest.fixture
def sample_keywords():
    """Return a list of sample Keyword objects for testing."""
    from models.keywords import Keyword, SearchIntent

    return [
        Keyword(
            term="executive leadership",
            volume=12000,
            cpc=8.50,
            competition=0.75,
            search_intent=SearchIntent.INFORMATIONAL,
            related_queries=["leadership training", "executive coaching"],
            people_also_ask=["What is executive leadership?", "How to develop leadership?"],
            serp_features=["featured_snippet", "paa", "knowledge_panel"],
            trends_interest=72,
            trends_momentum=0.15,
            source="serpapi",
        ),
        Keyword(
            term="leadership development programs",
            volume=8500,
            cpc=12.00,
            competition=0.68,
            search_intent=SearchIntent.COMMERCIAL,
            related_queries=["leadership programs", "corporate training"],
            people_also_ask=["Best leadership programs?"],
            serp_features=["paa"],
            trends_interest=65,
            trends_momentum=0.22,
            source="serpapi",
        ),
        Keyword(
            term="leadership coaching certification",
            volume=3200,
            cpc=15.75,
            competition=0.45,
            search_intent=SearchIntent.TRANSACTIONAL,
            related_queries=["coaching certification", "ICF certification"],
            people_also_ask=[],
            serp_features=[],
            trends_interest=58,
            trends_momentum=0.35,
            source="serpapi",
        ),
        Keyword(
            term="team building leadership",
            volume=None,
            trends_interest=42,
            trends_momentum=-0.05,
            source="serpapi_related",
        ),
        Keyword(
            term="change management training",
            volume=6800,
            competition=0.55,
            trends_interest=60,
            trends_momentum=0.18,
            source="serpapi_related",
        ),
    ]


@pytest.fixture
def sample_config():
    """Return sample config settings."""
    return {
        "enable_serpapi": True,
        "enable_trends": True,
        "no_network_mode": True,
        "seed_keywords": ["executive leadership"],
    }
