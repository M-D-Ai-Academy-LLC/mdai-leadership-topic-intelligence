"""Competitive Scraper agent — lightweight content intelligence from competitor sites."""

from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from loguru import logger

from agents.base_agent import BaseAgent
from core.config import settings
from models.base import AgentResponse
from models.competitors import Competitor, CompetitorContent

MOCK_COMPETITOR_DATA = {
    "hbr.org": {
        "name": "Harvard Business Review",
        "pages": [
            {"url": "https://hbr.org/topic/leadership", "title": "Leadership - HBR", "word_count": 2500},
            {"url": "https://hbr.org/topic/change-management", "title": "Change Management - HBR", "word_count": 1800},
            {"url": "https://hbr.org/topic/executive-leadership", "title": "Executive Leadership - HBR", "word_count": 3200},
        ],
    },
    "mckinsey.com": {
        "name": "McKinsey & Company",
        "pages": [
            {"url": "https://mckinsey.com/capabilities/people-and-organizational-performance", "title": "Leadership Development", "word_count": 4100},
            {"url": "https://mckinsey.com/featured-insights/leadership", "title": "Leadership Insights", "word_count": 2800},
        ],
    },
    "ccl.org": {
        "name": "Center for Creative Leadership",
        "pages": [
            {"url": "https://ccl.org/leadership-solutions", "title": "Leadership Solutions - CCL", "word_count": 1900},
            {"url": "https://ccl.org/articles/executive-coaching", "title": "Executive Coaching - CCL", "word_count": 1500},
            {"url": "https://ccl.org/articles/leadership-development", "title": "Leadership Development - CCL", "word_count": 2200},
            {"url": "https://ccl.org/articles/team-leadership", "title": "Team Leadership - CCL", "word_count": 1700},
        ],
    },
}


class CompetitiveScraperAgent(BaseAgent):
    """Scrapes competitor sites for content intelligence (lightweight, no Playwright)."""

    def __init__(self):
        super().__init__(name="CompetitiveScraper", model=settings.default_model)
        self.enabled = settings.enable_competitors

    async def process(self, input_data: Dict[str, Any] = None) -> AgentResponse:
        self.start_task()

        if not self.enabled:
            logger.info("Competitive scraping disabled via feature flag")
            return self.create_response(status="skipped", data={"competitors": [], "reason": "disabled"})

        competitors = []
        domains = settings.competitor_domains

        for domain in domains:
            logger.info(f"Analyzing competitor: {domain}")
            competitor = await self._analyze_competitor(domain)
            if competitor:
                competitors.append(competitor)

        return self.create_response(
            status="success",
            data={"competitors": [c.model_dump() for c in competitors]},
            metadata={"domains_analyzed": len(domains), "competitors_found": len(competitors)},
        )

    async def _analyze_competitor(self, domain: str) -> Optional[Competitor]:
        """Analyze a single competitor domain."""
        if settings.no_network_mode:
            return self._mock_competitor(domain)

        try:
            import requests
            from bs4 import BeautifulSoup

            # Try to fetch sitemap
            sitemap_url = f"https://{domain}/sitemap.xml"
            pages = []

            try:
                resp = requests.get(sitemap_url, timeout=10, headers={"User-Agent": "MDAI-TopicIntel/1.0"})
                if resp.status_code == 200 and "xml" in resp.headers.get("content-type", ""):
                    soup = BeautifulSoup(resp.text, "xml")
                    urls = [loc.text for loc in soup.find_all("loc")][:50]

                    for url in urls[:20]:  # Limit to 20 pages
                        page = await self._scrape_page(url)
                        if page:
                            pages.append(page)
            except Exception as e:
                logger.warning(f"Sitemap fetch failed for {domain}: {e}")

            # If no sitemap, try homepage
            if not pages:
                homepage = f"https://{domain}"
                page = await self._scrape_page(homepage)
                if page:
                    pages.append(page)

            topics = list(set(p.topic for p in pages if p.topic))

            return Competitor(
                domain=domain,
                name=domain.split(".")[0].title(),
                content_count=len(pages),
                top_topics=topics[:10],
                coverage_ratio=0.0,  # Calculated later by ContentGapAgent
            )

        except ImportError:
            logger.warning("requests/beautifulsoup4 not installed, using mock data")
            return self._mock_competitor(domain)
        except Exception as e:
            logger.error(f"Failed to analyze {domain}: {e}")
            return self._mock_competitor(domain)

    async def _scrape_page(self, url: str) -> Optional[CompetitorContent]:
        """Scrape a single page for content metadata."""
        try:
            import requests
            from bs4 import BeautifulSoup

            resp = requests.get(url, timeout=10, headers={"User-Agent": "MDAI-TopicIntel/1.0"})
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string if soup.title else ""
            text = soup.get_text(separator=" ", strip=True)
            word_count = len(text.split())

            # Simple topic extraction from title
            topic = None
            leadership_terms = ["leadership", "executive", "management", "coaching", "training", "development"]
            for term in leadership_terms:
                if term in title.lower():
                    topic = term.title()
                    break

            return CompetitorContent(
                url=url,
                title=title[:200],
                topic=topic,
                word_count=word_count,
            )

        except Exception as e:
            logger.debug(f"Failed to scrape {url}: {e}")
            return None

    def _mock_competitor(self, domain: str) -> Competitor:
        """Return mock competitor data for testing."""
        mock = MOCK_COMPETITOR_DATA.get(domain, {
            "name": domain.split(".")[0].title(),
            "pages": [{"url": f"https://{domain}", "title": f"{domain} Homepage", "word_count": 1000}],
        })
        return Competitor(
            domain=domain,
            name=mock.get("name", domain),
            content_count=len(mock.get("pages", [])),
            top_topics=["Leadership", "Management", "Training"],
            coverage_ratio=0.0,
        )
