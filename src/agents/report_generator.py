"""Report Generator agent — produces markdown reports with scoring analysis."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from agents.base_agent import BaseAgent
from contracts.report_generator import ReportInput, ReportOutput
from core.config import settings
from models.base import AgentResponse
from models.keywords import Keyword, KeywordCluster
from models.segments import IntentSegment
from models.topics import TopicCategory


class ReportGeneratorAgent(BaseAgent):
    """Generates markdown reports from keyword intelligence data."""

    def __init__(self):
        super().__init__(name="ReportGenerator", model=settings.default_model)

    async def process(self, input_data: ReportInput) -> AgentResponse:
        self.start_task()
        logger.info(f"Generating {input_data.config.output_format} report: {input_data.config.title}")

        sections = []

        # Executive Summary
        sections.append(self._build_executive_summary(input_data))

        # Top Keywords by Demand Signal
        if "top_keywords" in input_data.config.sections:
            sections.append(self._build_top_keywords(input_data.keywords))

        # Topic Clusters
        if "topic_clusters" in input_data.config.sections:
            sections.append(self._build_topic_clusters(input_data.clusters, input_data.topics))

        # Intent Segments
        if "intent_segments" in input_data.config.sections:
            sections.append(self._build_intent_segments(input_data.segments))

        # Opportunity Scores
        if "opportunity_scores" in input_data.config.sections:
            sections.append(self._build_opportunity_scores(input_data.topics))

        # Content Gaps
        if input_data.gaps:
            sections.append(self._build_content_gaps(input_data.gaps))

        # Momentum & Breakout Trends
        if "momentum_trends" in input_data.config.sections:
            sections.append(self._build_momentum_trends(input_data.keywords))

        # Assemble report
        content = self._assemble_report(input_data.config.title, input_data.config.query, sections)

        # Write to file
        filename = f"leadership_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = settings.reports_dir / filename
        filepath.write_text(content)
        logger.info(f"Report written to {filepath}")

        output = ReportOutput(
            content=content,
            format=input_data.config.output_format,
            path=str(filepath),
            metadata={"sections": len(sections), "keywords_analyzed": len(input_data.keywords)},
        )

        return self.create_response(status="success", data=output.model_dump(), metadata=output.metadata)

    def _calculate_demand_signal(self, kw: Keyword) -> float:
        """Calculate composite demand signal for a keyword."""
        w_trends = 0.30
        w_serp = 0.30
        w_paa = 0.20
        w_volume = 0.20

        trends_score = max(min(kw.trends_momentum or 0, 1.0), 0.0)
        serp_score = min(len(kw.serp_features) / 6, 1.0)
        paa_score = min(len(kw.people_also_ask) / 10, 1.0)
        volume_score = min((kw.volume or 0) / 10000, 1.0)

        signal = (trends_score * w_trends) + (serp_score * w_serp) + (paa_score * w_paa) + (volume_score * w_volume)
        return round(signal, 4)

    def _calculate_opportunity_score(self, demand: float, competition: Optional[float], cpc: Optional[float]) -> float:
        """Calculate opportunity score."""
        w_comp = 0.40
        w_cpc = 0.20
        comp = competition or 0.5
        cpc_norm = min((cpc or 0) / 50, 1.0)
        score = demand - (w_comp * comp) + (w_cpc * cpc_norm)
        return round(max(min(score, 1.0), 0.0), 4)

    def _build_executive_summary(self, data: ReportInput) -> str:
        """Build executive summary section."""
        return f"""## Executive Summary

- **Query**: {data.config.query}
- **Keywords Discovered**: {len(data.keywords)}
- **Topic Clusters**: {len(data.clusters)}
- **Intent Segments**: {len(data.segments)}
- **Content Gaps Identified**: {len(data.gaps)}
- **Report Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""

    def _build_top_keywords(self, keywords: List[Keyword]) -> str:
        """Build top keywords section ranked by demand signal."""
        scored = [(kw, self._calculate_demand_signal(kw)) for kw in keywords]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_20 = scored[:20]

        lines = ["## Top Keywords by Demand Signal\n"]
        lines.append("| Rank | Keyword | Demand Signal | Volume | Trends | PAA Count |")
        lines.append("|------|---------|--------------|--------|--------|-----------|")

        for i, (kw, demand) in enumerate(top_20, 1):
            vol = str(kw.volume) if kw.volume else "N/A"
            trends = str(kw.trends_interest) if kw.trends_interest else "N/A"
            paa = str(len(kw.people_also_ask))
            lines.append(f"| {i} | {kw.term} | {demand:.4f} | {vol} | {trends} | {paa} |")

        return "\n".join(lines) + "\n"

    def _build_topic_clusters(self, clusters: List[KeywordCluster], topics: List[TopicCategory]) -> str:
        """Build topic clusters section."""
        lines = ["## Topic Clusters\n"]
        lines.append("| Cluster | Keywords | Avg Demand | Top Keywords |")
        lines.append("|---------|----------|-----------|-------------|")

        sorted_clusters = sorted(clusters, key=lambda c: c.avg_demand_signal, reverse=True)
        for c in sorted_clusters:
            top_kws = ", ".join([kw.term for kw in c.keywords[:3]])
            lines.append(f"| {c.label} | {c.size} | {c.avg_demand_signal:.4f} | {top_kws} |")

        return "\n".join(lines) + "\n"

    def _build_intent_segments(self, segments: List[IntentSegment]) -> str:
        """Build intent segments section."""
        lines = ["## Intent Segments\n"]
        lines.append("| Segment | Keywords | Demand Signal | Example Queries |")
        lines.append("|---------|----------|--------------|-----------------|")

        for s in sorted(segments, key=lambda x: x.demand_signal, reverse=True):
            examples = ", ".join(s.example_queries[:3])
            lines.append(f"| {s.name} | {len(s.keywords)} | {s.demand_signal:.4f} | {examples} |")

        return "\n".join(lines) + "\n"

    def _build_opportunity_scores(self, topics: List[TopicCategory]) -> str:
        """Build opportunity scores section."""
        lines = ["## Opportunity Scores\n"]
        lines.append("| Topic | Demand | Opportunity | Gap Score |")
        lines.append("|-------|--------|------------|-----------|")

        for t in sorted(topics, key=lambda x: x.opportunity_score, reverse=True)[:15]:
            gap = f"{t.gap_score:.4f}" if t.gap_score is not None else "N/A"
            lines.append(f"| {t.name} | {t.demand_signal:.4f} | {t.opportunity_score:.4f} | {gap} |")

        return "\n".join(lines) + "\n"

    def _build_content_gaps(self, gaps: List[TopicCategory]) -> str:
        """Build content gaps section."""
        lines = ["## Content Gaps\n"]
        lines.append("| Topic | Gap Score | Opportunity | Keywords |")
        lines.append("|-------|-----------|------------|----------|")

        for g in sorted(gaps, key=lambda x: x.gap_score or 0, reverse=True)[:10]:
            gap = f"{g.gap_score:.4f}" if g.gap_score is not None else "N/A"
            kw_count = len(g.keywords)
            lines.append(f"| {g.name} | {gap} | {g.opportunity_score:.4f} | {kw_count} |")

        return "\n".join(lines) + "\n"

    def _build_momentum_trends(self, keywords: List[Keyword]) -> str:
        """Build momentum and breakout trends section."""
        trending = [(kw, kw.trends_momentum or 0) for kw in keywords if (kw.trends_momentum or 0) > 0]
        trending.sort(key=lambda x: x[1], reverse=True)

        lines = ["## Momentum & Breakout Trends\n"]
        lines.append("| Keyword | Momentum | Trends Interest | Status |")
        lines.append("|---------|----------|----------------|--------|")

        for kw, momentum in trending[:15]:
            interest = str(kw.trends_interest) if kw.trends_interest else "N/A"
            status = "BREAKOUT" if momentum > 1.0 else ("Rising" if momentum > 0.2 else "Stable")
            lines.append(f"| {kw.term} | {momentum:.4f} | {interest} | {status} |")

        return "\n".join(lines) + "\n"

    def _assemble_report(self, title: str, query: str, sections: List[str]) -> str:
        """Assemble the full report from sections."""
        header = f"""# {title}

**Query**: {query}
**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

---

"""
        return header + "\n".join(sections)
