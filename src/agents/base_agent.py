"""Base agent class with common functionality."""

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from loguru import logger

from core.config import settings
from models.base import AgentResponse


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, model: Optional[str] = None):
        self.name = name
        self.model = model or settings.default_model
        self.task_id = None
        self._start_time = None
        logger.info(f"Initialized {name} with model {self.model}")

    @abstractmethod
    async def process(self, input_data: Any) -> AgentResponse:
        pass

    def start_task(self) -> str:
        self.task_id = str(uuid4())
        self._start_time = time.time()
        logger.info(f"{self.name} started task {self.task_id}")
        return self.task_id

    def end_task(self) -> float:
        if self._start_time:
            processing_time = time.time() - self._start_time
            logger.info(f"{self.name} completed task {self.task_id} in {processing_time:.2f}s")
            return processing_time
        return 0.0

    def create_response(
        self,
        status: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        processing_time = self.end_task()
        return AgentResponse(
            agent_name=self.name,
            task_id=self.task_id or "unknown",
            status=status,
            data=data,
            metadata=metadata or {},
            timestamp=datetime.utcnow(),
            processing_time_seconds=processing_time,
        )

    async def retry_with_backoff(
        self,
        func,
        *args,
        max_retries: Optional[int] = None,
        **kwargs,
    ):
        max_retries = max_retries or settings.max_retries
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"{self.name} failed after {max_retries} attempts: {e}")
                    raise
                wait_time = (2 ** attempt) * settings.rate_limit_delay
                logger.warning(f"{self.name} attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
