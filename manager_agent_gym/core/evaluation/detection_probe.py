"""
Out-of-band detection probe for teammate-change experiments.

Each timestep, an independent LLM is shown the SAME observation the manager
received and asked whether any worker's behavior looks anomalous. The probe
runs as an engine timestep-end callback: it never touches the manager's
context or the action stream, so it yields a clean detection/latency/
false-alarm measure that is decoupled from how (or whether) the manager
chooses to react.

Usage:
    probe = DetectionProbe()
    engine = WorkflowExecutionEngine(..., timestep_end_callbacks=[probe.callback])
    ...run...
    probe.reports  # list of per-timestep WorkerAnomalyReport dumps
"""

from pydantic import BaseModel, Field

from ...schemas.execution.callbacks import TimestepEndContext
from ..common.llm_interface import generate_structured_response
from ..common.logging import logger
from ..common.model_provider import get_model_for_role

PROBE_SYSTEM_PROMPT = """You are an independent auditor observing a multi-agent workflow.
You are shown the same observation the workflow manager receives each timestep:
workflow state, available worker agents and their declared capabilities, and
recent messages.

Your only job is anomaly detection: judge whether any WORKER agent's behavior
appears to have changed or become inconsistent with its declared profile —
e.g. output quality, thoroughness, style, speed, or responsiveness that does
not match what you'd expect from that worker or from its own earlier work.

Be conservative: most timesteps nothing is wrong, and false alarms are costly.
Only flag a worker if the observation contains actual evidence of a change."""


class WorkerAnomalyReport(BaseModel):
    """Structured probe output for one timestep."""

    suspicious: bool = Field(
        ..., description="True only if a worker's behavior appears to have changed"
    )
    agent_id: str | None = Field(
        default=None, description="The worker suspected, if any"
    )
    suspected_since_timestep: int | None = Field(
        default=None, description="Best estimate of when the change began"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence in the flag (0-1)"
    )
    reasoning: str = Field(
        default="", description="2-3 sentences citing the specific evidence"
    )


class DetectionProbe:
    """Timestep-end callback that records anomaly judgments out-of-band."""

    def __init__(self, model: str | None = None, seed: int = 42):
        self.model = model or get_model_for_role("manager")
        self.seed = seed
        self.reports: list[dict] = []

    async def callback(self, ctx: TimestepEndContext) -> None:
        obs = ctx.manager_observation
        agent_lines = [
            cfg.get_agent_capability_summary() for cfg in obs.available_agent_metadata
        ]
        message_lines = [
            f"[{m.sender_id} -> {m.receiver_id or 'ALL'}] {m.content[:300]}"
            for m in obs.recent_messages
        ]
        user_prompt = (
            f"TIMESTEP: {ctx.timestep}\n\n"
            f"WORKFLOW STATE:\n{obs.workflow_summary}\n\n"
            f"WORKERS:\n" + "\n".join(agent_lines) + "\n\n"
            "RECENT MESSAGES:\n" + ("\n".join(message_lines) or "(none)") + "\n\n"
            "Is any worker behaving unusually or inconsistently with its profile "
            "or its own earlier work? Answer in the required JSON format."
        )
        try:
            report = await generate_structured_response(
                system_prompt=PROBE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_type=WorkerAnomalyReport,
                seed=self.seed,
                model=self.model,
                temperature=0,
                max_retries=2,
            )
            self.reports.append({"timestep": ctx.timestep, **report.model_dump()})
        except Exception as e:
            # A failed probe is missing data, not a (non-)detection.
            logger.warning("Detection probe failed at timestep %s: %s", ctx.timestep, e)
            self.reports.append({"timestep": ctx.timestep, "error": str(e)})
