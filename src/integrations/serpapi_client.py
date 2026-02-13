"""SerpAPI integration client for SERP intelligence and keyword discovery."""

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from core.config import settings


MOCK_SERP_RESPONSE = {
    "search_parameters": {"q": "executive leadership", "engine": "google"},
    "organic_results": [
        {"position": 1, "title": "Executive Leadership Programs", "link": "https://example.com/leadership", "snippet": "Top executive leadership programs..."},
        {"position": 2, "title": "Leadership Development Training", "link": "https://example.com/training", "snippet": "Corporate leadership development..."},
        {"position": 3, "title": "Best Leadership Courses 2026", "link": "https://example.com/courses", "snippet": "The best leadership courses for executives..."},
    ],
    "related_searches": [
        {"query": "executive leadership training"},
        {"query": "leadership development programs"},
        {"query": "corporate leadership coaching"},
        {"query": "executive leadership certification"},
        {"query": "leadership skills for managers"},
    ],
    "related_questions": [
        {"question": "What is executive leadership?", "snippet": "Executive leadership involves..."},
        {"question": "How to develop leadership skills?", "snippet": "Leadership skills can be developed through..."},
        {"question": "What are the best leadership programs?", "snippet": "The top leadership programs include..."},
        {"question": "How much do leadership programs cost?", "snippet": "Leadership program costs range from..."},
    ],
    "search_information": {"total_results": 285000000},
}


class SerpApiClient:
    """Client for SerpAPI search intelligence."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.serpapi_key
        self.base_url = "https://serpapi.com/search"
        self.enabled = settings.enable_serpapi and not settings.no_network_mode

    async def search(self, query: str, **params) -> Dict[str, Any]:
        """Execute a search query via SerpAPI."""
        if not self.enabled or settings.no_network_mode:
            logger.info(f"SerpAPI disabled or no-network mode, returning mock for: {query}")
            mock = MOCK_SERP_RESPONSE.copy()
            mock["search_parameters"]["q"] = query
            return mock

        if not self.api_key:
            logger.warning("No SerpAPI key configured, returning mock data")
            mock = MOCK_SERP_RESPONSE.copy()
            mock["search_parameters"]["q"] = query
            return mock

        request_params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": params.get("num", 20),
            **{k: v for k, v in params.items() if k != "num"},
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(self.base_url, params=request_params)
            response.raise_for_status()
            return response.json()

    async def search_keywords(self, query: str, num: int = 100) -> List[Dict[str, Any]]:
        """Get SERP data including organic results, related searches, and PAA."""
        result = await self.search(query, num=min(num, 100))

        keywords = []
        # Extract from organic results
        for item in result.get("organic_results", []):
            keywords.append({
                "term": query,
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "position": item.get("position"),
            })

        # Extract related searches as additional keywords
        for item in result.get("related_searches", []):
            keywords.append({
                "term": item.get("query", ""),
                "source": "related_search",
            })

        return keywords

    async def get_related_searches(self, query: str) -> List[str]:
        """Get related search queries."""
        result = await self.search(query)
        return [item.get("query", "") for item in result.get("related_searches", [])]

    async def get_people_also_ask(self, query: str) -> List[str]:
        """Get People Also Ask questions."""
        result = await self.search(query)
        return [item.get("question", "") for item in result.get("related_questions", [])]

    async def get_serp_features(self, query: str) -> Dict[str, Any]:
        """Analyze SERP features for a query."""
        result = await self.search(query)

        features = {
            "has_featured_snippet": "answer_box" in result,
            "has_knowledge_panel": "knowledge_graph" in result,
            "paa_count": len(result.get("related_questions", [])),
            "organic_count": len(result.get("organic_results", [])),
            "related_searches_count": len(result.get("related_searches", [])),
            "total_results": result.get("search_information", {}).get("total_results", 0),
        }

        # Calculate SERP richness score (0-1)
        max_features = 6
        feature_count = sum([
            features["has_featured_snippet"],
            features["has_knowledge_panel"],
            min(features["paa_count"] / 4, 1),
            min(features["organic_count"] / 10, 1),
            min(features["related_searches_count"] / 5, 1),
            1 if features["total_results"] > 1000000 else 0,
        ])
        features["serp_richness"] = round(feature_count / max_features, 3)

        return features
