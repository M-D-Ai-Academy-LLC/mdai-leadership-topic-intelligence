"""SQLAlchemy models and database initialization for SQLite storage."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.types import JSON

from core.config import settings

Base = declarative_base()


class RawApiResponse(Base):
    """Stores raw API responses for caching and reproducibility."""

    __tablename__ = "raw_api_responses"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), nullable=False, index=True)
    config_hash = Column(String(64), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # serpapi, trends, gsc
    query = Column(String(500), nullable=False)
    response_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class NormalizedKeyword(Base):
    """Normalized keyword data extracted from raw API responses."""

    __tablename__ = "normalized_keywords"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), nullable=False, index=True)
    term = Column(String(500), nullable=False, index=True)
    volume = Column(Integer, nullable=True)
    cpc = Column(Float, nullable=True)
    competition = Column(Float, nullable=True)
    search_intent = Column(String(50), nullable=True)
    trends_interest = Column(Integer, nullable=True)
    trends_momentum = Column(Float, nullable=True)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DerivedCluster(Base):
    """Derived topic clusters from keyword analysis."""

    __tablename__ = "derived_clusters"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), nullable=False, index=True)
    cluster_id = Column(Integer, nullable=False)
    label = Column(String(255), nullable=False)
    keyword_count = Column(Integer, default=0)
    avg_demand_signal = Column(Float, default=0.0)
    top_intent = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompetitorCrawl(Base):
    """Competitor content crawl outputs."""

    __tablename__ = "competitor_crawls"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(64), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    url = Column(String(2000), nullable=False)
    title = Column(String(500), default="")
    topic = Column(String(255), nullable=True)
    word_count = Column(Integer, nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)


def init_database(url: Optional[str] = None) -> tuple:
    """Initialize the database and return engine + session maker."""
    db_url = url or settings.database_url
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session_local


def get_session(session_maker: sessionmaker) -> Session:
    """Get a database session."""
    db = session_maker()
    try:
        yield db
    finally:
        db.close()
