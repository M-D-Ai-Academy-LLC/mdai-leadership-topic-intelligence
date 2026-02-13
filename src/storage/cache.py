"""Cache manager for API response deduplication and reproducibility."""

from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy.orm import Session

from storage.database import RawApiResponse


class CacheManager:
    """Manages caching of API responses using SQLite storage."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _get_session(self) -> Session:
        return self.session_factory()

    def is_cache_hit(self, source: str, query: str, config_hash: str) -> bool:
        """Check if a cached response exists for this source + query + config."""
        session = self._get_session()
        try:
            count = (
                session.query(RawApiResponse)
                .filter_by(source=source, query=query, config_hash=config_hash)
                .count()
            )
            return count > 0
        finally:
            session.close()

    def get_cached_response(
        self, source: str, query: str, config_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a cached API response."""
        session = self._get_session()
        try:
            record = (
                session.query(RawApiResponse)
                .filter_by(source=source, query=query, config_hash=config_hash)
                .order_by(RawApiResponse.created_at.desc())
                .first()
            )
            if record:
                logger.debug(f"Cache hit: {source}/{query}")
                return record.response_json
            return None
        finally:
            session.close()

    def store_response(
        self,
        run_id: str,
        config_hash: str,
        source: str,
        query: str,
        response: Dict[str, Any],
    ) -> None:
        """Store an API response in the cache."""
        session = self._get_session()
        try:
            record = RawApiResponse(
                run_id=run_id,
                config_hash=config_hash,
                source=source,
                query=query,
                response_json=response,
            )
            session.add(record)
            session.commit()
            logger.debug(f"Cached response: {source}/{query} (run={run_id})")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cache response: {e}")
        finally:
            session.close()
