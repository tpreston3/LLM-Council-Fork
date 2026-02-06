"""
In-memory storage for async council deliberation jobs.

WARNING: In-memory store → only safe with ONE uvicorn worker!
Do NOT use --workers > 1 or behind a load balancer.
For multi-process / production → switch to Redis / SQLite.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from pydantic import BaseModel


class CouncilStage(str, Enum):
    """Stages of the council deliberation process."""
    QUEUED = "queued"
    FIRST_OPINIONS = "first-opinions"
    PEER_REVIEW = "peer-review"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    FAILED = "failed"


class CouncilState(BaseModel):
    """State of a single council deliberation job."""
    id: str
    prompt: str
    status: CouncilStage = CouncilStage.QUEUED
    current_stage: CouncilStage = CouncilStage.QUEUED
    created_at: str
    updated_at: Optional[str] = None
    config: dict = {}
    stage1: dict = {}  # model → {"text": "...", "timestamp": "..."}
    stage2: dict = {}  # reviews & rankings
    stage3: dict = {}  # chairman model + final synthesis
    error: Optional[str] = None
    error_detail: Optional[str] = None
    failed_stage: Optional[str] = None

    def get_progress_description(self) -> str:
        """Return a human-readable progress string."""
        if self.status == CouncilStage.COMPLETED:
            return "Completed"
        if self.status == CouncilStage.FAILED:
            return f"Failed at {self.failed_stage or 'unknown stage'}"
        if not self.stage1:
            return "Preparing first opinions..."
        done = len(self.stage1)
        total = len(self.config.get("models", []))
        if self.current_stage == CouncilStage.FIRST_OPINIONS:
            return f"First opinions: {done}/{total} models answered"
        if self.current_stage == CouncilStage.PEER_REVIEW:
            return f"Peer review in progress ({done}/{total} answers processed)"
        if self.current_stage == CouncilStage.SYNTHESIS:
            return "Chairman synthesizing final answer..."
        return f"{self.current_stage.value} in progress"

    def to_markdown(self) -> str:
        """Render the result as Markdown."""
        lines = [
            f"# Council {self.id}",
            "",
            f"**Status:** {self.status.value}",
            f"**Query:** {self.prompt}",
            "",
        ]
        if self.status == CouncilStage.FAILED:
            lines.append(f"> **Error:** {self.error or 'Unknown error'}")
            return "\n".join(lines)

        if self.stage3:
            lines.append("## Final Answer")
            lines.append(self.stage3.get("response", ""))
            lines.append("")

        if self.stage1:
            lines.append("## First Round Opinions")
            for model, data in self.stage1.items():
                lines.append(f"### {model}")
                lines.append(data.get("text", ""))
                lines.append("")

        return "\n".join(lines)

    def to_json_result(self) -> dict:
        """Return full state as JSON-serializable dict."""
        return self.model_dump(mode="json")


class InMemoryStore:
    """
    Thread-safe in-memory storage for council jobs.

    WARNING: Only safe with a single uvicorn worker!
    """
    _data: Dict[str, CouncilState] = {}
    _lock = asyncio.Lock()
    _cleanup_interval_hours = 24

    @classmethod
    async def save(cls, state: CouncilState):
        """Save or update a council state."""
        async with cls._lock:
            cls._data[state.id] = state

    @classmethod
    async def get(cls, council_id: str) -> Optional[CouncilState]:
        """Retrieve a council state by ID."""
        async with cls._lock:
            return cls._data.get(council_id)

    @classmethod
    async def update_partial(cls, council_id: str, **kwargs):
        """Atomically update specific fields of a council state."""
        async with cls._lock:
            if state := cls._data.get(council_id):
                for k, v in kwargs.items():
                    if hasattr(state, k):
                        setattr(state, k, v)
                state.updated_at = datetime.utcnow().isoformat() + "Z"

    @classmethod
    async def cleanup_old_jobs(cls, max_age_hours: int = 24):
        """Remove completed/failed jobs older than max_age_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        async with cls._lock:
            to_delete = []
            for cid, state in cls._data.items():
                if state.status in (CouncilStage.COMPLETED, CouncilStage.FAILED):
                    try:
                        created = datetime.fromisoformat(state.created_at.replace("Z", "+00:00"))
                        if created.replace(tzinfo=None) < cutoff:
                            to_delete.append(cid)
                    except ValueError:
                        pass  # Skip malformed dates
            for cid in to_delete:
                del cls._data[cid]
            return len(to_delete)

    @classmethod
    async def list_all(cls) -> list:
        """List all council jobs (for debugging)."""
        async with cls._lock:
            return list(cls._data.values())
