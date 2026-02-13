"""Google Trends integration client for directional demand signals."""

from typing import Any, Dict, List, Optional

from loguru import logger

from core.config import settings


MOCK_TRENDS_RESPONSE = {
    "interest_over_time": {
        "executive leadership": [45, 52, 48, 55, 60, 58, 62, 65, 70, 68, 72, 75],
        "dates": [
            "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08",
            "2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02",
        ],
    },
    "related_queries": {
        "top": [
            {"query": "executive leadership program", "value": 100},
            {"query": "leadership development", "value": 85},
            {"query": "leadership training", "value": 72},
            {"query": "corporate leadership", "value": 65},
            {"query": "leadership coaching", "value": 58},
        ],
        "rising": [
            {"query": "ai leadership training", "value": 450},
            {"query": "remote leadership skills", "value": 300},
            {"query": "inclusive leadership", "value": 200},
        ],
    },
}


class GoogleTrendsClient:
    """Client for Google Trends directional demand data."""

    def __init__(self):
        self.enabled = settings.enable_trends and not settings.no_network_mode
        self._pytrends = None

    def _get_pytrends(self):
        """Lazy-load pytrends to avoid import errors in no-network mode."""
        if self._pytrends is None and self.enabled:
            try:
                from pytrends.request import TrendReq
                self._pytrends = TrendReq(hl="en-US", tz=360)
            except ImportError:
                logger.warning("pytrends not installed, falling back to mock data")
                self.enabled = False
        return self._pytrends

    def get_interest_over_time(
        self, keywords: List[str], timeframe: str = "today 12-m"
    ) -> Dict[str, Any]:
        """Get interest over time for keywords (normalized 0-100)."""
        if not self.enabled or settings.no_network_mode:
            logger.info(f"Trends disabled or no-network mode, returning mock for: {keywords}")
            return self._mock_interest(keywords)

        pt = self._get_pytrends()
        if pt is None:
            return self._mock_interest(keywords)

        try:
            # pytrends only supports up to 5 keywords at a time
            batch_size = 5
            results = {}
            for i in range(0, len(keywords), batch_size):
                batch = keywords[i : i + batch_size]
                pt.build_payload(batch, timeframe=timeframe)
                df = pt.interest_over_time()
                if not df.empty:
                    for kw in batch:
                        if kw in df.columns:
                            results[kw] = df[kw].tolist()
                    results["dates"] = [d.strftime("%Y-%m") for d in df.index]
            return {"interest_over_time": results}
        except Exception as e:
            logger.error(f"Google Trends API error: {e}")
            return self._mock_interest(keywords)

    def get_related_queries(self, keyword: str) -> Dict[str, Any]:
        """Get related queries for a keyword."""
        if not self.enabled or settings.no_network_mode:
            return MOCK_TRENDS_RESPONSE["related_queries"]

        pt = self._get_pytrends()
        if pt is None:
            return MOCK_TRENDS_RESPONSE["related_queries"]

        try:
            pt.build_payload([keyword], timeframe="today 12-m")
            related = pt.related_queries()
            result = {"top": [], "rising": []}
            if keyword in related:
                top_df = related[keyword].get("top")
                if top_df is not None and not top_df.empty:
                    result["top"] = top_df.to_dict("records")
                rising_df = related[keyword].get("rising")
                if rising_df is not None and not rising_df.empty:
                    result["rising"] = rising_df.to_dict("records")
            return result
        except Exception as e:
            logger.error(f"Google Trends related queries error: {e}")
            return MOCK_TRENDS_RESPONSE["related_queries"]

    def get_interest_by_region(self, keyword: str) -> Dict[str, int]:
        """Get interest by region for a keyword."""
        if not self.enabled or settings.no_network_mode:
            return {"United States": 100, "United Kingdom": 72, "Canada": 65, "Australia": 58, "India": 45}

        pt = self._get_pytrends()
        if pt is None:
            return {}

        try:
            pt.build_payload([keyword], timeframe="today 12-m")
            df = pt.interest_by_region(resolution="COUNTRY")
            if not df.empty:
                return df[keyword].to_dict()
            return {}
        except Exception as e:
            logger.error(f"Google Trends region error: {e}")
            return {}

    def calculate_momentum(self, values: List[int]) -> float:
        """Calculate momentum: (recent_avg - prior_avg) / prior_avg."""
        if len(values) < 6:
            return 0.0
        midpoint = len(values) // 2
        prior_avg = sum(values[:midpoint]) / midpoint
        recent_avg = sum(values[midpoint:]) / (len(values) - midpoint)
        if prior_avg == 0:
            return 1.0 if recent_avg > 0 else 0.0
        momentum = (recent_avg - prior_avg) / prior_avg
        return round(max(min(momentum, 1.0), -1.0), 4)

    def detect_breakout(self, values: List[int], related_queries: Optional[Dict] = None) -> bool:
        """Detect breakout trend (>5000% growth or momentum > 1.0 with steep slope)."""
        if related_queries:
            rising = related_queries.get("rising", [])
            for q in rising:
                val = q.get("value", 0)
                if isinstance(val, str) and "Breakout" in val:
                    return True
                if isinstance(val, (int, float)) and val >= 5000:
                    return True
        momentum = self.calculate_momentum(values)
        if momentum > 1.0:
            return True
        return False

    def _mock_interest(self, keywords: List[str]) -> Dict[str, Any]:
        """Return mock interest data for testing."""
        mock = {"interest_over_time": {}}
        base_values = MOCK_TRENDS_RESPONSE["interest_over_time"].get(
            "executive leadership", [50] * 12
        )
        for kw in keywords:
            mock["interest_over_time"][kw] = base_values
        mock["interest_over_time"]["dates"] = MOCK_TRENDS_RESPONSE["interest_over_time"]["dates"]
        return mock
