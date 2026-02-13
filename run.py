"""Main orchestrator and CLI for the Leadership Topic Intelligence system."""

import asyncio
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

import click
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.keyword_researcher import KeywordResearcherAgent
from agents.topic_clusterer import TopicClustererAgent
from agents.intent_segmenter import IntentSegmenterAgent
from agents.report_generator import ReportGeneratorAgent
from agents.competitive_scraper import CompetitiveScraperAgent
from agents.content_gap import ContentGapAgent
from contracts.keyword_researcher import KeywordResearchInput
from contracts.topic_clusterer import TopicClusterInput
from contracts.intent_segmenter import IntentSegmentInput
from contracts.content_gap import ContentGapInput
from contracts.report_generator import ReportInput
from core.config import settings
from models.reports import ReportConfig
from storage.database import init_database
from storage.cache import CacheManager

console = Console()


class Orchestrator:
    """Coordinates all agents in the topic intelligence pipeline."""

    def __init__(self):
        self.agents = {
            "keyword_researcher": KeywordResearcherAgent(),
            "topic_clusterer": TopicClustererAgent(),
            "intent_segmenter": IntentSegmenterAgent(),
            "report_generator": ReportGeneratorAgent(),
            "competitive_scraper": CompetitiveScraperAgent(),
            "content_gap": ContentGapAgent(),
        }
        self.results = {}
        self.run_id = str(uuid4())[:8]
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # Initialize storage
        self.engine, self.session_factory = init_database()
        self.cache = CacheManager(self.session_factory)

        # Setup logging
        if settings.log_file:
            logger.add(
                settings.log_file,
                rotation="10 MB",
                retention="30 days",
                level=settings.log_level,
            )

    def _config_hash(self, query: str) -> str:
        """Generate a config hash for cache key."""
        config_str = json.dumps({
            "query": query,
            "enable_serpapi": settings.enable_serpapi,
            "enable_trends": settings.enable_trends,
            "seed_keywords": settings.seed_keywords,
        }, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:12]

    async def run_pipeline(self, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full topic intelligence pipeline."""
        query = input_data.get("query", "executive leadership")
        config_hash = self._config_hash(query)

        console.print(f"[bold cyan]Starting {task_type} pipeline...[/bold cyan]")
        console.print(f"[dim]Run ID: {self.run_id} | Config Hash: {config_hash}[/dim]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Phase 1: Keyword Research
            task = progress.add_task("[cyan]Discovering keywords...", total=1)
            queries = [query] + settings.seed_keywords
            kw_input = KeywordResearchInput(
                queries=queries,
                max_results=input_data.get("max_results", 100),
                include_trends=settings.enable_trends,
            )
            kw_result = await self.agents["keyword_researcher"].process(kw_input)
            self.results["keyword_research"] = kw_result
            progress.update(task, completed=1)

            keywords_data = kw_result.data.get("keywords", [])
            from models.keywords import Keyword
            keywords = [Keyword(**kw) if isinstance(kw, dict) else kw for kw in keywords_data]

            # Phase 2: Topic Clustering
            if task_type in ("cluster", "full") and len(keywords) >= 3:
                task = progress.add_task("[green]Clustering topics...", total=1)
                cluster_input = TopicClusterInput(keywords=keywords)
                cluster_result = await self.agents["topic_clusterer"].process(cluster_input)
                self.results["topic_clustering"] = cluster_result
                progress.update(task, completed=1)

            # Phase 3: Intent Segmentation
            if task_type == "full":
                task = progress.add_task("[yellow]Segmenting by intent...", total=1)
                segment_input = IntentSegmentInput(keywords=keywords)
                segment_result = await self.agents["intent_segmenter"].process(segment_input)
                self.results["intent_segmentation"] = segment_result
                progress.update(task, completed=1)

            # Phase 4: Competitive Analysis (if enabled)
            competitors = []
            if task_type in ("gaps", "full") and settings.enable_competitors:
                task = progress.add_task("[magenta]Analyzing competitors...", total=1)
                comp_result = await self.agents["competitive_scraper"].process()
                self.results["competitive_analysis"] = comp_result
                comp_data = comp_result.data.get("competitors", [])
                from models.competitors import Competitor
                competitors = [Competitor(**c) if isinstance(c, dict) else c for c in comp_data]
                progress.update(task, completed=1)

            # Phase 5: Content Gap Analysis
            topics_data = self.results.get("topic_clustering", {})
            if isinstance(topics_data, object) and hasattr(topics_data, "data"):
                topics_data = topics_data.data
            topics_list = topics_data.get("topics", []) if isinstance(topics_data, dict) else []
            from models.topics import TopicCategory
            topics = [TopicCategory(**t) if isinstance(t, dict) else t for t in topics_list]

            gaps = []
            if task_type in ("gaps", "full") and topics and competitors:
                task = progress.add_task("[red]Finding content gaps...", total=1)
                gap_input = ContentGapInput(topics=topics, competitors=competitors)
                gap_result = await self.agents["content_gap"].process(gap_input)
                self.results["content_gaps"] = gap_result
                gap_data = gap_result.data.get("gaps", [])
                gaps = [TopicCategory(**g) if isinstance(g, dict) else g for g in gap_data]
                progress.update(task, completed=1)

            # Phase 6: Report Generation
            task = progress.add_task("[blue]Generating report...", total=1)

            clusters_data = self.results.get("topic_clustering", {})
            if hasattr(clusters_data, "data"):
                clusters_data = clusters_data.data
            clusters_list = clusters_data.get("clusters", []) if isinstance(clusters_data, dict) else []
            from models.keywords import KeywordCluster
            clusters = [KeywordCluster(**c) if isinstance(c, dict) else c for c in clusters_list]

            segments_data = self.results.get("intent_segmentation", {})
            if hasattr(segments_data, "data"):
                segments_data = segments_data.data
            segments_list = segments_data.get("segments", []) if isinstance(segments_data, dict) else []
            from models.segments import IntentSegment
            segments = [IntentSegment(**s) if isinstance(s, dict) else s for s in segments_list]

            report_config = ReportConfig(
                title=f"Leadership Topic Intelligence: {query}",
                query=query,
                report_type=task_type,
            )
            report_input = ReportInput(
                config=report_config,
                keywords=keywords,
                clusters=clusters,
                topics=topics,
                segments=segments,
                gaps=gaps,
            )
            report_result = await self.agents["report_generator"].process(report_input)
            self.results["report"] = report_result
            progress.update(task, completed=1)

        # Save session
        session_file = settings.output_dir / f"session_{self.session_id}.json"
        with open(session_file, "w") as f:
            json.dump({
                "session_id": self.session_id,
                "run_id": self.run_id,
                "config_hash": config_hash,
                "task_type": task_type,
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "results_summary": {
                    "keywords": len(keywords),
                    "clusters": len(clusters),
                    "segments": len(segments),
                    "competitors": len(competitors),
                    "gaps": len(gaps),
                },
            }, f, indent=2, default=str)

        return {
            "session_id": self.session_id,
            "run_id": self.run_id,
            "results": self.results,
            "report_path": report_result.data.get("path", ""),
        }


@click.command()
@click.option("--task", "-t", type=click.Choice(["research", "cluster", "gaps", "full"]), default="full", help="Pipeline task type")
@click.option("--query", "-q", default="executive leadership", help="Search query")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--dev", is_flag=True, help="Development mode")
def main(task: str, query: str, output: Optional[str], dev: bool):
    """M&D AI Academy — Leadership Topic Intelligence System."""
    if dev:
        settings.debug_mode = True

    if output:
        settings.output_dir = Path(output)
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    console.print("[bold cyan]M&D AI Academy — Leadership Topic Intelligence[/bold cyan]")
    console.print(f"Task: {task} | Query: {query}\n")

    input_data = {
        "query": query,
        "max_results": 100,
    }

    orchestrator = Orchestrator()

    try:
        results = asyncio.run(orchestrator.run_pipeline(task, input_data))

        console.print("\n[bold green]Pipeline completed successfully![/bold green]\n")

        # Results table
        table = Table(title="Results Summary")
        table.add_column("Phase", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Output", style="yellow")

        for phase, result in results.get("results", {}).items():
            status = result.status if hasattr(result, "status") else "unknown"
            table.add_row(phase.replace("_", " ").title(), status.upper(), "")

        console.print(table)

        report_path = results.get("report_path", "")
        if report_path:
            console.print(f"\n[bold]Report:[/bold] {report_path}")

        console.print(f"\n[dim]Session: {results.get('session_id')} | Run: {results.get('run_id')}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
