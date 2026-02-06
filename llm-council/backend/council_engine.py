"""
Background task engine for running council deliberations asynchronously.
"""

import asyncio
from datetime import datetime
from typing import Optional
import traceback

from .storage_memory import InMemoryStore, CouncilState, CouncilStage
from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL
from .council import parse_ranking_from_text, calculate_aggregate_rankings


# Timeout for each stage (10 minutes)
STAGE_TIMEOUT_SECONDS = 600


async def run_council_deliberation(council_id: str):
    """
    Run the full 3-stage council deliberation as a background task.
    Updates the InMemoryStore as each stage completes.

    Args:
        council_id: The ID of the council job to run.
    """
    try:
        state = await InMemoryStore.get(council_id)
        if not state:
            return

        # --- STAGE 1: First Opinions ---
        await InMemoryStore.update_partial(
            council_id,
            status=CouncilStage.FIRST_OPINIONS,
            current_stage=CouncilStage.FIRST_OPINIONS,
        )

        try:
            stage1_results = await asyncio.wait_for(
                _run_stage1(state.prompt, council_id),
                timeout=STAGE_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            await _mark_failed(council_id, "Stage 1 timed out", "first-opinions")
            return

        if not stage1_results:
            await _mark_failed(council_id, "No models responded in Stage 1", "first-opinions")
            return

        # --- STAGE 2: Peer Review ---
        await InMemoryStore.update_partial(
            council_id,
            current_stage=CouncilStage.PEER_REVIEW,
        )

        try:
            stage2_results, label_to_model = await asyncio.wait_for(
                _run_stage2(state.prompt, stage1_results, council_id),
                timeout=STAGE_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            await _mark_failed(council_id, "Stage 2 timed out", "peer-review")
            return

        # --- STAGE 3: Synthesis ---
        await InMemoryStore.update_partial(
            council_id,
            current_stage=CouncilStage.SYNTHESIS,
        )

        try:
            stage3_result = await asyncio.wait_for(
                _run_stage3(state.prompt, stage1_results, stage2_results),
                timeout=STAGE_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            await _mark_failed(council_id, "Stage 3 timed out", "synthesis")
            return

        # --- COMPLETED ---
        aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

        await InMemoryStore.update_partial(
            council_id,
            status=CouncilStage.COMPLETED,
            current_stage=CouncilStage.COMPLETED,
            stage3={
                "model": stage3_result.get("model", CHAIRMAN_MODEL),
                "response": stage3_result.get("response", ""),
                "label_to_model": label_to_model,
                "aggregate_rankings": aggregate_rankings,
            },
        )

    except Exception as exc:
        tb = traceback.format_exc()
        await _mark_failed(council_id, str(exc), "unknown", tb)


async def _mark_failed(council_id: str, error: str, stage: str, detail: Optional[str] = None):
    """Mark a council job as failed."""
    await InMemoryStore.update_partial(
        council_id,
        status=CouncilStage.FAILED,
        error=error,
        failed_stage=stage,
        error_detail=detail,
    )


async def _run_stage1(prompt: str, council_id: str) -> list:
    """Run Stage 1: Collect individual model responses."""
    messages = [{"role": "user", "content": prompt}]
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    results = []
    for model, response in responses.items():
        if response is not None:
            text = response.get("content", "")
            ts = datetime.utcnow().isoformat() + "Z"
            results.append({"model": model, "response": text})

            # Update state incrementally
            state = await InMemoryStore.get(council_id)
            if state:
                state.stage1[model] = {"text": text, "timestamp": ts}
                await InMemoryStore.save(state)

    return results


async def _run_stage2(prompt: str, stage1_results: list, council_id: str) -> tuple:
    """Run Stage 2: Each model ranks the anonymized responses."""
    # Create anonymized labels
    labels = [chr(65 + i) for i in range(len(stage1_results))]  # A, B, C, ...
    label_to_model = {
        f"Response {label}": result["model"]
        for label, result in zip(labels, stage1_results)
    }

    # Build ranking prompt
    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {prompt}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Now provide your evaluation and ranking:"""

    messages = [{"role": "user", "content": ranking_prompt}]
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    results = []
    for model, response in responses.items():
        if response is not None:
            full_text = response.get("content", "")
            parsed = parse_ranking_from_text(full_text)
            results.append({
                "model": model,
                "ranking": full_text,
                "parsed_ranking": parsed,
            })

    # Update state
    state = await InMemoryStore.get(council_id)
    if state:
        state.stage2 = {
            "results": results,
            "label_to_model": label_to_model,
        }
        await InMemoryStore.save(state)

    return results, label_to_model


async def _run_stage3(prompt: str, stage1_results: list, stage2_results: list) -> dict:
    """Run Stage 3: Chairman synthesizes a final response."""
    stage1_text = "\n\n".join([
        f"Model: {r['model']}\nResponse: {r['response']}"
        for r in stage1_results
    ])

    stage2_text = "\n\n".join([
        f"Model: {r['model']}\nRanking: {r['ranking']}"
        for r in stage2_results
    ])

    chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have provided responses to a user's question, and then ranked each other's responses.

Original Question: {prompt}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task as Chairman is to synthesize all of this information into a single, comprehensive, accurate answer to the user's original question. Consider:
- The individual responses and their insights
- The peer rankings and what they reveal about response quality
- Any patterns of agreement or disagreement

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""

    messages = [{"role": "user", "content": chairman_prompt}]
    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        return {
            "model": CHAIRMAN_MODEL,
            "response": "Error: Unable to generate final synthesis.",
        }

    return {
        "model": CHAIRMAN_MODEL,
        "response": response.get("content", ""),
    }
