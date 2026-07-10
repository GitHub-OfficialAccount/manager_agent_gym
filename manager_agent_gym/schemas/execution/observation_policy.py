"""
Observation policy: the declared contract for what a manager agent can perceive.

The manager's observation is the measurement instrument for any experiment on
manager behavior — results are only interpretable relative to an explicit
statement of what the manager could see. This object is that statement: it is
passed to the engine, applied when observations are built, and should be
serialized into run manifests alongside results.

Redaction default: worker system prompts are hidden. A worker's system prompt
is its private policy; exposing it in the observation would let a manager
trivially "detect" behavior changes by reading the policy instead of observing
behavior.
"""

from typing import Literal

from pydantic import BaseModel, Field

WorkerMetadataLevel = Literal["id_only", "capabilities", "full"]


class ObservationPolicy(BaseModel):
    """Declares what enters a ManagerObservation.

    Tier fields for passive quality digests and monitor flags will be added
    when those observation channels are implemented (M2).
    """

    expose_worker_system_prompts: bool = Field(
        default=False,
        description=(
            "Include workers' system prompts in observed agent metadata. Keep False "
            "for any behavior-observation experiment; True reveals policy changes "
            "directly."
        ),
    )
    worker_metadata: WorkerMetadataLevel = Field(
        default="capabilities",
        description=(
            "How much per-worker metadata the manager sees: 'id_only' (just agent "
            "ids/types), 'capabilities' (ids + description + declared capabilities; "
            "matches baseline behavior), or 'full' (entire config, minus system "
            "prompt unless separately exposed)."
        ),
    )
    message_window: int = Field(
        default=10,
        ge=0,
        description="How many recent messages the manager sees each timestep",
    )

    def redact_agent_config(self, config):
        """Return a copy of an agent config filtered to this policy."""
        updates: dict = {}
        if not self.expose_worker_system_prompts:
            updates["system_prompt"] = "[REDACTED]"
        if self.worker_metadata == "id_only":
            updates["agent_description"] = ""
            updates["agent_capabilities"] = []
        return config.model_copy(update=updates) if updates else config
