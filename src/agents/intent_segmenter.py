"""Intent Segmenter agent — classifies keywords by query intent."""

import re
from typing import Any, Dict, List

from loguru import logger

from agents.base_agent import BaseAgent
from contracts.intent_segmenter import IntentSegmentInput, IntentSegmentOutput
from core.config import settings
from models.base import AgentResponse
from models.keywords import Keyword
from models.segments import AudiencePersona, IntentSegment


# Intent pattern definitions for leadership domain
INTENT_PATTERNS = {
    "training": {
        "patterns": [r"\btraining\b", r"\bcourse\b", r"\bworkshop\b", r"\bprogram\b", r"\bclass\b", r"\bbootcamp\b"],
        "description": "Structured learning programs and formal training",
    },
    "coaching": {
        "patterns": [r"\bcoach\b", r"\bcoaching\b", r"\bmentor\b", r"\bmentoring\b", r"\b1[- ]on[- ]1\b"],
        "description": "One-on-one or small group coaching and mentoring",
    },
    "certification": {
        "patterns": [r"\bcertif", r"\bcredential\b", r"\baccredit\b", r"\bdiploma\b", r"\bdegree\b"],
        "description": "Formal credentials and certification programs",
    },
    "change_management": {
        "patterns": [r"\bchange\s+manage", r"\btransform", r"\brestructur", r"\breorganiz"],
        "description": "Organizational change and transformation leadership",
    },
    "team_building": {
        "patterns": [r"\bteam\s+build", r"\bteamwork\b", r"\bcollabora", r"\bteam\s+lead"],
        "description": "Team development and collaborative leadership",
    },
    "executive_development": {
        "patterns": [r"\bexecutive\b", r"\bc-suite\b", r"\bceo\b", r"\bcfo\b", r"\bcto\b", r"\bsenior\s+lead"],
        "description": "Senior and C-suite executive development",
    },
    "skills_assessment": {
        "patterns": [r"\bassess", r"\bevaluat", r"\bmeasur", r"\b360\b", r"\bfeedback\b", r"\bcompeten"],
        "description": "Leadership skills assessment and evaluation",
    },
    "thought_leadership": {
        "patterns": [r"\bthought\s+lead", r"\binsight", r"\btrend", r"\bfuture\s+of", r"\bstrateg"],
        "description": "Industry insights, trends, and strategic thinking",
    },
}


class IntentSegmenterAgent(BaseAgent):
    """Segments keywords by query intent using pattern matching."""

    def __init__(self):
        super().__init__(name="IntentSegmenter", model=settings.default_model)

    async def process(self, input_data: IntentSegmentInput) -> AgentResponse:
        self.start_task()
        logger.info(f"Segmenting {len(input_data.keywords)} keywords by intent")

        # Classify each keyword
        intent_buckets: Dict[str, List[Keyword]] = {intent: [] for intent in INTENT_PATTERNS}
        intent_buckets["other"] = []

        for kw in input_data.keywords:
            matched = False
            for intent_name, intent_def in INTENT_PATTERNS.items():
                for pattern in intent_def["patterns"]:
                    if re.search(pattern, kw.term.lower()):
                        intent_buckets[intent_name].append(kw)
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                intent_buckets["other"].append(kw)

        # Build IntentSegment objects
        segments = []
        for intent_name, keywords in intent_buckets.items():
            if not keywords:
                continue

            desc = INTENT_PATTERNS.get(intent_name, {}).get("description", "Other/unclassified queries")
            demand = sum(kw.trends_momentum or 0 for kw in keywords) / len(keywords) if keywords else 0

            segment = IntentSegment(
                name=intent_name.replace("_", " ").title(),
                description=desc,
                query_intents=[intent_name],
                keywords=[kw.term for kw in keywords],
                demand_signal=round(demand, 4),
                example_queries=[kw.term for kw in keywords[:5]],
            )
            segments.append(segment)

        # Generate personas (lightweight, no LLM needed for V0)
        personas = []
        if input_data.generate_personas:
            personas = self._generate_basic_personas(segments)

        output = IntentSegmentOutput(
            segments=segments,
            personas=personas,
            metadata={"total_segments": len(segments), "unclassified": len(intent_buckets.get("other", []))},
        )

        logger.info(f"Created {len(segments)} intent segments")
        return self.create_response(status="success", data=output.model_dump(), metadata=output.metadata)

    def _generate_basic_personas(self, segments: List[IntentSegment]) -> List[AudiencePersona]:
        """Generate basic audience personas from intent segments (no LLM, rule-based V0)."""
        persona_map = {
            "Training": AudiencePersona(
                name="The Corporate Learner",
                description="HR/L&D professional sourcing training programs for their organization",
                pain_points=["Finding quality programs", "Justifying training ROI", "Scaling across teams"],
                goals=["Upskill workforce", "Improve retention", "Build leadership pipeline"],
                preferred_content_types=["case studies", "webinars", "whitepapers"],
                intent_segments=["training"],
            ),
            "Coaching": AudiencePersona(
                name="The Growth-Minded Executive",
                description="Senior leader seeking personal coaching for career advancement",
                pain_points=["Isolation at the top", "Blind spots in leadership style", "Work-life balance"],
                goals=["Accelerate career growth", "Improve executive presence", "Build strategic thinking"],
                preferred_content_types=["podcasts", "books", "1-on-1 sessions"],
                intent_segments=["coaching"],
            ),
            "Certification": AudiencePersona(
                name="The Credential Seeker",
                description="Professional pursuing formal leadership credentials for career mobility",
                pain_points=["Credential overload", "Cost of programs", "Time commitment"],
                goals=["Earn recognized certification", "Stand out in job market", "Validate expertise"],
                preferred_content_types=["program comparisons", "reviews", "ROI calculators"],
                intent_segments=["certification"],
            ),
            "Executive Development": AudiencePersona(
                name="The C-Suite Aspirant",
                description="Mid-to-senior leader preparing for executive roles",
                pain_points=["Readiness gap for C-suite", "Board-level communication", "Strategic vs tactical"],
                goals=["Secure promotion", "Build executive network", "Develop board presence"],
                preferred_content_types=["executive briefings", "peer roundtables", "retreats"],
                intent_segments=["executive_development"],
            ),
        }

        personas = []
        for segment in segments:
            if segment.name in persona_map:
                personas.append(persona_map[segment.name])

        return personas
