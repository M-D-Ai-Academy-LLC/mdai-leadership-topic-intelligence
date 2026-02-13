"""Content Gap agent — identifies underserved topics with high demand."""

from typing import Any, Dict, List

from loguru import logger

from agents.base_agent import BaseAgent
from contracts.content_gap import ContentGapInput, ContentGapOutput
from core.config import settings
from models.base import AgentResponse
from models.competitors import Competitor
from models.topics import TopicCategory


class ContentGapAgent(BaseAgent):
    """Analyzes content gaps between demand signals and competitor coverage."""

    def __init__(self):
        super().__init__(name="ContentGap", model=settings.default_model)

    async def process(self, input_data: ContentGapInput) -> AgentResponse:
        self.start_task()
        logger.info(
            f"Analyzing content gaps: {len(input_data.topics)} topics vs {len(input_data.competitors)} competitors"
        )

        # Calculate coverage ratio per topic
        gaps = []
        ranked = []

        for topic in input_data.topics:
            coverage = self._calculate_coverage(topic, input_data.competitors)
            gap_score = topic.opportunity_score * (1 - coverage)

            gap_topic = topic.model_copy(
                update={"gap_score": round(gap_score, 4)}
            )
            gaps.append(gap_topic)

            ranked.append({
                "topic": topic.name,
                "demand_signal": topic.demand_signal,
                "opportunity_score": topic.opportunity_score,
                "competitor_coverage": round(coverage, 4),
                "gap_score": round(gap_score, 4),
            })

        # Sort by gap score descending
        gaps.sort(key=lambda t: t.gap_score or 0, reverse=True)
        ranked.sort(key=lambda x: x["gap_score"], reverse=True)

        output = ContentGapOutput(
            gaps=gaps[:10],  # Top 10 gaps
            ranked_opportunities=ranked,
            metadata={
                "total_topics_analyzed": len(input_data.topics),
                "total_competitors": len(input_data.competitors),
                "top_gap_score": ranked[0]["gap_score"] if ranked else 0,
            },
        )

        logger.info(f"Identified {len(gaps)} content gaps, top score: {output.metadata.get('top_gap_score', 0):.4f}")
        return self.create_response(status="success", data=output.model_dump(), metadata=output.metadata)

    def _calculate_coverage(self, topic: TopicCategory, competitors: List[Competitor]) -> float:
        """Calculate what fraction of competitors cover this topic."""
        if not competitors:
            return 0.0

        covering = 0
        topic_terms = set(kw.lower() for kw in topic.keywords)
        topic_name_lower = topic.name.lower()

        for comp in competitors:
            comp_topics = set(t.lower() for t in comp.top_topics)
            # Check if competitor covers this topic
            if topic_name_lower in comp_topics:
                covering += 1
            elif topic_terms & comp_topics:
                covering += 0.5  # Partial coverage

        return covering / len(competitors)
