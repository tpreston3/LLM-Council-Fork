"""
Council REST API router.

Endpoints:
    POST /query       - Start a new council deliberation
    GET /{council_id} - Get status/result of a deliberation
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import secrets

from ..storage_memory import InMemoryStore, CouncilState, CouncilStage
from ..council_engine import run_council_deliberation
from ..config import COUNCIL_MODELS


router = APIRouter(prefix="/api/v1/council", tags=["council"])


class QueryRequest(BaseModel):
    """Request body for starting a new council deliberation."""
    prompt: str = Field(..., description="The question to ask the council")
    models: Optional[List[str]] = Field(
        default=None,
        description="Optional list of model identifiers (defaults to config)"
    )
    max_tokens: Optional[int] = Field(default=None, description="Max tokens per response")
    temperature: Optional[float] = Field(default=None, description="Temperature for sampling")
    format: Optional[str] = Field(
        default="markdown",
        description="Output format: text, markdown, or json"
    )


class QueryResponse(BaseModel):
    """Response after starting a council deliberation."""
    council_id: str
    status: str
    created_at: str
    message: str


class StatusResponse(BaseModel):
    """Response for checking council status."""
    council_id: str
    status: str
    stage: Optional[str] = None
    progress: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    error: Optional[str] = None
    error_detail: Optional[str] = None


def _generate_council_id() -> str:
    """Generate a unique council ID with timestamp."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    suffix = secrets.token_hex(4)
    return f"council_{timestamp}_{suffix}"


@router.post("/query", response_model=QueryResponse, status_code=202)
async def start_council_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new council deliberation.

    Returns immediately with a council_id that can be used to poll for results.
    """
    council_id = _generate_council_id()
    now = datetime.utcnow().isoformat() + "Z"

    # Create initial state
    state = CouncilState(
        id=council_id,
        prompt=request.prompt,
        status=CouncilStage.QUEUED,
        current_stage=CouncilStage.QUEUED,
        created_at=now,
        config={
            "models": request.models or COUNCIL_MODELS,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "format": request.format or "markdown",
        },
    )

    await InMemoryStore.save(state)

    # Start background task
    background_tasks.add_task(run_council_deliberation, council_id)

    return QueryResponse(
        council_id=council_id,
        status="queued",
        created_at=now,
        message=f"Deliberation started – check progress at /api/v1/council/{council_id}",
    )


@router.get("/{council_id}")
async def get_council_status(
    council_id: str,
    format: str = Query(default="json", description="Output format: text, markdown, or json")
):
    """
    Get the status and/or result of a council deliberation.

    - If still running: returns status and progress
    - If completed: returns full result in requested format
    - If failed: returns error information
    """
    state = await InMemoryStore.get(council_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Council not found")

    # If still running, return status only
    if state.status not in (CouncilStage.COMPLETED, CouncilStage.FAILED):
        return StatusResponse(
            council_id=council_id,
            status=state.status.value,
            stage=state.current_stage.value,
            progress=state.get_progress_description(),
            created_at=state.created_at,
            updated_at=state.updated_at,
        )

    # If failed, return error info
    if state.status == CouncilStage.FAILED:
        if format == "json":
            return StatusResponse(
                council_id=council_id,
                status="failed",
                stage=state.failed_stage,
                progress=None,
                created_at=state.created_at,
                updated_at=state.updated_at,
                error=state.error,
                error_detail=state.error_detail,
            )
        else:
            return PlainTextResponse(
                f"# Council {council_id} - FAILED\n\nError: {state.error}\n\n{state.error_detail or ''}",
                media_type="text/plain" if format == "text" else "text/markdown",
            )

    # Completed - return full result
    if format == "json":
        return state.to_json_result()
    elif format == "markdown":
        return PlainTextResponse(state.to_markdown(), media_type="text/markdown")
    else:  # text
        return PlainTextResponse(state.to_markdown(), media_type="text/plain")
