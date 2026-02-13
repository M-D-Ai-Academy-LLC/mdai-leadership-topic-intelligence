"""Configuration management for the leadership topic intelligence system."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    serpapi_key: Optional[str] = None

    # Model Configuration
    default_model: str = "gpt-4o-mini"
    research_model: str = "claude-sonnet-4-5-20250929"
    keyword_model: str = "gpt-4o-mini"
    clustering_model: str = "gpt-4o-mini"

    # Agent Configuration
    max_retries: int = 3
    request_timeout: int = 30
    rate_limit_delay: float = 1.0

    # Paths
    output_dir: Path = Path("./outputs")
    reports_dir: Path = Path("./reports")
    visualizations_dir: Path = Path("./visualizations")
    logs_dir: Path = Path("./logs")
    data_dir: Path = Path("./data")

    # Brand Configuration
    brand_primary_color: str = "#5CBDBD"
    brand_secondary_color: str = "#3A9B9B"
    brand_tertiary_color: str = "#2D7A7A"
    brand_font_family: str = "Inter, system-ui, sans-serif"

    # Database
    database_url: str = "sqlite:///./data/topic_intel.db"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = Path("./logs/topic_intel.log")

    # Feature Flags
    enable_serpapi: bool = True
    enable_trends: bool = True
    enable_gsc: bool = False
    enable_competitors: bool = True
    enable_news: bool = False
    enable_firmographics: bool = False
    no_network_mode: bool = False

    # Seed Keywords
    seed_keywords: List[str] = [
        "executive leadership",
        "leadership development",
        "leadership training",
        "corporate leadership programs",
        "leadership coaching",
    ]

    # Competitor Domains
    competitor_domains: List[str] = [
        "hbr.org",
        "mckinsey.com",
        "ccl.org",
        "kornferry.com",
        "ddiworld.com",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_path in [
            self.output_dir,
            self.reports_dir,
            self.visualizations_dir,
            self.logs_dir,
            self.data_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @property
    def brand_colors(self) -> dict:
        """Get brand colors as a dictionary."""
        return {
            "primary": self.brand_primary_color,
            "secondary": self.brand_secondary_color,
            "tertiary": self.brand_tertiary_color,
        }


settings = Settings()
