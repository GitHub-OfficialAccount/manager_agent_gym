import asyncio
import json

import pytest
from pydantic import BaseModel

from manager_agent_gym.core.common.run_trace import (
    RunTraceRecorder,
    record_run_event,
    trace_scope,
)


class _Result(BaseModel):
    value: int


def test_run_trace_is_opt_in_and_bulk_writes_json(tmp_path) -> None:
    record_run_event("ignored", {"value": 0})
    recorder = RunTraceRecorder(metadata={"condition": "silent"})

    with recorder.activate(), trace_scope(
        timestep=3, actor_type="manager", actor_id="structured_manager"
    ):
        record_run_event("decision", _Result(value=7))

    path = tmp_path / "run.json"
    recorder.write_json(path, scores={"r_check": 0.75})
    bundle = json.loads(path.read_text())

    assert bundle["schema_version"] == "1.0"
    assert bundle["metadata"] == {"condition": "silent"}
    assert bundle["scores"] == {"r_check": 0.75}
    assert bundle["events"] == [{
        "sequence": 0,
        "timestamp": bundle["events"][0]["timestamp"],
        "event_type": "decision",
        "timestep": 3,
        "actor_type": "manager",
        "actor_id": "structured_manager",
        "payload": {"value": 7},
    }]


@pytest.mark.asyncio
async def test_run_trace_sequences_parallel_events_at_capture_time() -> None:
    recorder = RunTraceRecorder()

    async def emit(actor_id: str) -> None:
        await asyncio.sleep(0)
        record_run_event("worker_event", actor_id=actor_id)

    with recorder.activate():
        await asyncio.gather(emit("a"), emit("b"), emit("c"))

    assert [event["sequence"] for event in recorder.events] == [0, 1, 2]
    assert {event["actor_id"] for event in recorder.events} == {"a", "b", "c"}


@pytest.mark.asyncio
async def test_structured_llm_call_records_exact_request_and_response(monkeypatch) -> None:
    from manager_agent_gym.core.common import llm_interface

    class _Completions:
        async def create(self, **_kwargs):
            return _Result(value=9)

    class _Client:
        class _Chat:
            completions = _Completions()

        chat = _Chat()

    monkeypatch.setattr(llm_interface, "_get_openai_client", lambda **_kwargs: _Client())
    recorder = RunTraceRecorder()

    with recorder.activate(), trace_scope(actor_type="manager", timestep=4):
        result = await llm_interface.generate_structured_response(
            system_prompt="exact system prompt",
            user_prompt="exact observation prompt",
            response_type=_Result,
            seed=42,
            model="gpt-4o",
            temperature=0,
        )

    assert result.value == 9
    request, response = recorder.events
    assert request["event_type"] == "structured_llm_request"
    assert request["actor_type"] == "manager"
    assert request["timestep"] == 4
    assert request["payload"]["messages"] == [
        {"role": "system", "content": "exact system prompt"},
        {"role": "user", "content": "exact observation prompt"},
    ]
    assert request["payload"]["response_schema"] == _Result.model_json_schema()
    assert response["event_type"] == "structured_llm_response"
    assert response["payload"]["parsed_response"] == {"value": 9}
