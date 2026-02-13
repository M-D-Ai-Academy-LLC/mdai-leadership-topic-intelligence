"""Keyword Researcher agent — discovers keywords via SerpAPI and Google Trends."""

from typing import Any, Dict, List, Optional

from loguru import logger

from agents.base_agent import BaseAgent
from contracts.keyword_researcher import KeywordResearchInput, KeywordResearchOutput
from core.config import settings
from integrations.google_trends_client import GoogleTrendsClient
from integrations.serpapi_client import SerpApiClient
from models.base import AgentResponse
from models.keywords import Keyword


class KeywordResearcherAgent(BaseAgent):
    """Discovers and enriches keywords from multiple search intelligence sources."""

    def __init__(self, serpapi_client: Optional[SerpApiClient] = None, trends_client: Optional[GoogleTrendsClient] = None):
        super().__init__(name="KeywordResearcher", model=settings.keyword_model)
        self.serpapi = serpapi_client or SerpApiClient()
        self.trends = trends_client or GoogleTrendsClient()

    async def process(self, input_data: KeywordResearchInput) -> AgentResponse:
        self.start_task()
        logger.info(f"Starting keyword research for {len(input_data.queries)} queries")

        all_keywords: List[Keyword] = []
        seen_terms: set = set()

        for query in input_data.queries:
            # Get SERP data
            serp_keywords = await self._research_serp(query)
            for kw in serp_keywords:
                if kw.term.lower() not in seen_terms:
                    seen_terms.add(kw.term.lower())
                    all_keywords.append(kw)

            # Get trends data if enabled
            if input_data.include_trends:
                trends_data = self._enrich_with_trends(query, all_keywords)

        output = KeywordResearchOutput(
            keywords=all_keywords,
            total_discovered=len(all_keywords),
            metadata={
                "queries_processed": len(input_data.queries),
                "sources": ["serpapi", "trends"] if input_data.include_trends else ["serpapi"],
            },
        )

        return self.create_response(
            status="success",
            data=output.model_dump(),
            metadata=output.metadata,
        )

    async def _research_serp(self, query: str) -> List[Keyword]:
        """Research a single query via SerpAPI."""
        keywords = []

        try:
            # Get related searches
            related = await self.serpapi.get_related_searches(query)
            for term in related:
                keywords.append(Keyword(term=term, source="serpapi_related"))

            # Get PAA questions
            paa = await self.serpapi.get_people_also_ask(query)

            # Get SERP features for the main query
            features = await self.serpapi.get_serp_features(query)

            # Create main keyword entry
            main_kw = Keyword(
                term=query,
                people_also_ask=paa,
                serp_features=list(features.keys()),
                source="serpapi",
            )
            keywords.insert(0, main_kw)

        except Exception as e:
            logger.error(f"SerpAPI research failed for '{query}': {e}")
            keywords.append(Keyword(term=query, source="serpapi_fallback"))

        return keywords

    def _enrich_with_trends(self, query: str, keywords: List[Keyword]) -> None:
        """Enrich keywords with Google Trends data."""
        try:
            trends_data = self.trends.get_interest_over_time([query])
            interest_values = trends_data.get("interest_over_time", {}).get(query, [])

            if interest_values:
                momentum = self.trends.calculate_momentum(interest_values)
                current_interest = interest_values[-1] if interest_values else None

                for kw in keywords:
                    if kw.term.lower() == query.lower():
                        kw.trends_interest = current_interest
                        kw.trends_momentum = momentum
                        break

        except Exception as e:
            logger.error(f"Trends enrichment failed for '{query}': {e}")
