"""Optional in-memory event capture for offline execution inspection."""

from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any, Iterator

from pydantic import BaseModel

if TYPE_CHECKING:
    from ...schemas.execution.callbacks import TimestepEndContext


_active_recorder: ContextVar[Any] = ContextVar(
    "active_run_trace_recorder", default=None
)
_trace_context: ContextVar[dict[str, Any]] = ContextVar(
    "run_trace_context", default={}
)


def _jsonable(value: Any) -> Any:
    """Convert SDK and Pydantic values to structures accepted by json.dump."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            return _jsonable(model_dump(mode="json"))
        except TypeError:
            return _jsonable(model_dump())
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _jsonable(to_dict())
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return str(value)


class RunTraceRecorder:
    """Collect ordered events in memory and write one offline run bundle."""

    schema_version = "1.0"

    def __init__(self, metadata: dict[str, Any] | None = None) -> None:
        self.metadata = _jsonable(metadata or {})
        self.events: list[dict[str, Any]] = []
        self._next_sequence = 0
        self._lock = Lock()

    @contextmanager
    def activate(self) -> Iterator[RunTraceRecorder]:
        """Make this recorder available to execution code in the current context."""
        token = _active_recorder.set(self)
        try:
            yield self
        finally:
            _active_recorder.reset(token)

    def record(
        self,
        event_type: str,
        payload: Any = None,
        **fields: Any,
    ) -> dict[str, Any]:
        with self._lock:
            sequence = self._next_sequence
            self._next_sequence += 1
            event = {
                "sequence": sequence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                **_jsonable(_trace_context.get()),
                **_jsonable(fields),
                "payload": _jsonable(payload),
            }
            self.events.append(event)
        return event

    async def timestep_callback(self, ctx: TimestepEndContext) -> None:
        """Capture the native end-of-timestep result, including its full snapshot."""
        self.record(
            "timestep_completed",
            timestep=ctx.timestep,
            actor_type="environment",
            actor_id="workflow_engine",
            payload=ctx.execution_result,
        )

    def bundle(self, **sections: Any) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "metadata": self.metadata,
            "events": list(self.events),
            **_jsonable(sections),
        }

    def write_json(self, path: Path, **sections: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as file:
            json.dump(self.bundle(**sections), file, indent=2)


@contextmanager
def trace_scope(**fields: Any) -> Iterator[None]:
    """Attach correlation fields to events emitted inside this context."""
    merged = {**_trace_context.get(), **fields}
    token = _trace_context.set(merged)
    try:
        yield
    finally:
        _trace_context.reset(token)


def record_run_event(event_type: str, payload: Any = None, **fields: Any) -> None:
    """Record an event when tracing is active; otherwise do nothing."""
    recorder = _active_recorder.get()
    if recorder is not None:
        recorder.record(event_type, payload, **fields)
