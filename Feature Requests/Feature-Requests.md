Proposal for **REST API** to your LLM Council FastAPI backend that supports:

- Starting a new council deliberation (POST)
- Checking progress / getting current state (GET)
- Returning results in flexible formats (text, markdown, JSON)

### 1. Proposed Endpoints

```text
POST   /api/v1/council/query           → Start new deliberation
GET    /api/v1/council/{council_id}    → Get status + result (when ready)
```

Both endpoints will support format selection via query parameter:

```
?format=text|markdown|json    (default: markdown)
```

### 2. Recommended Request / Response Shapes

**POST /api/v1/council/query**

```json
// Request body (JSON)
{
  "prompt": "What is the best way to learn Rust in 2026?",
  "models": ["anthropic/claude-4-opus", "openai/gpt-5", "google/gemini-2.0-pro", "xai/grok-3"],   // optional – defaults from config
  "max_tokens": 1200,           // optional
  "temperature": 0.7,           // optional
  "format": "markdown"          // optional: text | markdown | json (affects final synthesis only)
}
```

**Response (202 Accepted)**

```json
{
  "council_id": "council_20260105_2143_abc123",
  "status": "queued",           // queued | running | completed | failed
  "created_at": "2026-01-05T21:43:12Z",
  "message": "Deliberation started – check progress at /api/v1/council/council_20260105_2143_abc123"
}
```

**GET /api/v1/council/{council_id}?format=markdown**

Possible responses depending on state:

- **Still running / queued**

```json
{
  "council_id": "council_...",
  "status": "running",
  "stage": "peer-review",           // first-opinions | peer-review | synthesis | done | failed
  "progress": "3/4 models answered • 2/4 reviews completed",
  "created_at": "...",
  "updated_at": "..."
}
```

- **Completed – format=markdown** (default, nice for humans)

```text
# Final Answer – LLM Council

**Query:** What is the best way to learn Rust in 2026?

**Synthesized conclusion** (by chairman Claude-4-Opus)

The most effective path combines official resources, project-based learning and spaced repetition...

## First Round Opinions
### Grok-3
...

### GPT-5
...

## Peer Review Highlights
- Highest ranked answer: Grok-3 (avg score 8.7/10)
- Most criticized: Gemini (style too verbose)

## Raw Votes
...
```

- **Completed – format=json**

```json
{
  "council_id": "...",
  "status": "completed",
  "prompt": "...",
  "final_answer": {
    "text": "The most effective path...",
    "markdown": "# Final Answer ...\n...",
    "sources": ["stage1_grok", "stage1_claude", ...]
  },
  "stage1": {
    "answers": {
      "grok-3": { "text": "...", "timestamp": "..." },
      ...
    }
  },
  "stage2": {
    "reviews": { ... },
    "rankings": { ... }
  },
  "stage3": {
    "chairman_model": "claude-4-opus",
    "synthesis": "..."
  },
  "metadata": {
    "completed_at": "...",
    "duration_seconds": 187
  }
}
```

### 3. Quick Recommendations / Decisions You Need to Make

| Aspect               | Suggestion                              | Alternatives                     |
|----------------------|------------------------------------------|----------------------------------|
| Persistence          | Redis / SQLite                          | In-memory (dev only), file-system, PostgreSQL |
| Background runner    | FastAPI `BackgroundTasks`               | Celery, RQ, dramatiq             |
| Council ID format    | short timestamp + random                | UUID only, nanoID                |
| Rate limiting        | Add later with slowapi                  | —                                |
| Auth                 | Add API key header later                | JWT, none for local use          |
| Streaming            | Optional future GET with SSE            | —                                |

### 4. Next Steps (smallest useful increment)

1. Make `run_council_deliberation` update state in-place (or via pub/sub)

Here's a realistic, practical way to make `run_council_deliberation` **update the shared state** so the GET `/council/{council_id}` endpoint can show live progress.

The two most common & reasonable approaches for a local/personal project in 2026 are:

1. **In-memory mutable dict + lock** (simplest, good enough for single-worker local usage)

### Option 1: In-memory store + asyncio.Lock (recommended for quick start)

```python
# backend/storage.py
from typing import Dict
from datetime import datetime
import asyncio
from pydantic import BaseModel

class CouncilStage(str, Enum):
    QUEUED = "queued"
    FIRST_OPINIONS = "first-opinions"
    PEER_REVIEW = "peer-review"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    FAILED = "failed"

class CouncilState(BaseModel):
    id: str
    prompt: str
    status: CouncilStage = CouncilStage.QUEUED
    current_stage: CouncilStage = CouncilStage.QUEUED
    created_at: str
    updated_at: str | None = None
    config: dict
    stage1: dict = {}           # model → {"text": "...", "timestamp": "..."}
    stage2: dict = {}           # reviews & rankings
    stage3: dict = {}           # chairman model + final synthesis
    error: str | None = None

    def get_progress_description(self) -> str:
        if self.status in (CouncilStage.COMPLETED, CouncilStage.FAILED):
            return self.status
        if not self.stage1:
            return "Preparing first opinions..."
        done = len(self.stage1)
        total = len(self.config.get("models", []))
        if self.current_stage == CouncilStage.FIRST_OPINIONS:
            return f"First opinions: {done}/{total} models answered"
        if self.current_stage == CouncilStage.PEER_REVIEW:
            # simplistic – improve later
            return f"Peer review in progress ({done}/{total} answers processed)"
        return f"{self.current_stage} in progress"

    def to_markdown(self) -> str:
        # implement nice markdown rendering here (as in your earlier example)
        return f"# Council {self.id}\n\n**Status:** {self.status}\n..."

    def to_json_result(self) -> dict:
        return self.model_dump(mode="json")


class InMemoryStore:
    _data: Dict[str, CouncilState] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def save(cls, state: CouncilState):
        async with cls._lock:
            cls._data[state.id] = state

    @classmethod
    async def get(cls, council_id: str) -> CouncilState | None:
        async with cls._lock:
            return cls._data.get(council_id)

    @classmethod
    async def update_partial(cls, council_id: str, **kwargs):
        """Atomic-ish partial update"""
        async with cls._lock:
            if state := cls._data.get(council_id):
                for k, v in kwargs.items():
                    if hasattr(state, k):
                        setattr(state, k, v)
                state.updated_at = datetime.utcnow().isoformat() + "Z"
```

Now the background function becomes:

```python
# backend/council_engine.py
import asyncio
from .storage import InMemoryStore, CouncilState, CouncilStage
from .llm import call_openrouter  # your own wrapper

async def run_council_deliberation(council_id: str, request: QueryRequest):
    try:
        state = await InMemoryStore.get(council_id)
        if not state:
            return

        await InMemoryStore.update_partial(
            council_id,
            status=CouncilStage.FIRST_OPINIONS,
            current_stage=CouncilStage.FIRST_OPINIONS,
            updated_at=datetime.utcnow().isoformat() + "Z"
        )

        # Stage 1
        models = state.config["models"]
        tasks = []
        for model in models:
            async def get_answer(m=model):
                try:
                    text = await call_openrouter(m, state.prompt, state.config)
                    ts = datetime.utcnow().isoformat() + "Z"
                    async with InMemoryStore._lock:
                        s = await InMemoryStore.get(council_id)
                        s.stage1[m] = {"text": text, "timestamp": ts}
                        await InMemoryStore.save(s)  # or just update_partial
                except Exception as e:
                    # log & continue
                    pass

            tasks.append(get_answer())

        await asyncio.gather(*tasks, return_exceptions=True)

        # move to next stage
        await InMemoryStore.update_partial(
            council_id,
            current_stage=CouncilStage.PEER_REVIEW,
            updated_at=...
        )

        # Stage 2 – peer review (similar pattern – gather anonymous reviews & rankings)

        # Stage 3 – synthesis

        # Final
        await InMemoryStore.update_partial(
            council_id,
            status=CouncilStage.COMPLETED,
            current_stage=CouncilStage.COMPLETED,
            # fill stage3, etc.
        )

    except Exception as exc:
        await InMemoryStore.update_partial(
            council_id,
            status=CouncilStage.FAILED,
            error=str(exc)
        )
```

**Important notes about Option 1**

- Works fine with **one uvicorn worker** (`uvicorn main:app --port 8001`)
- Breaks with **multiple workers** (`--workers 4`) because each process has its own memory
- Use only for local dev / single-user setup

