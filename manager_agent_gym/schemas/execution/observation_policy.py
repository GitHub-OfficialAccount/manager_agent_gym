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

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field, PrivateAttr

if TYPE_CHECKING:
    from ...core.communication.service import CommunicationService

WorkerMetadataLevel = Literal["id_only", "capabilities", "full"]
ObservationAidMode = Literal["none", "generic_summary"]


class WorkerObservationDisclosure(BaseModel):
    """A scheduled change to one worker's manager-visible projection."""

    timestep: int = Field(ge=0)
    agent_id: str
    capability_override: list[str] | None = Field(
        default=None,
        description=(
            "Capabilities shown after this disclosure. None removes any prior "
            "override and exposes the worker's current canonical capabilities."
        ),
    )
    announce: bool = False
    announcement: str | None = None


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
    quality_digest: str = Field(
        default="none",
        description=(
            "Per-worker quality signal in the observation: 'none' (blind) or "
            "'per_worker' (a recent-correctness summary per worker). The detection "
            "channel for teammate-change experiments; populated by the engine."
        ),
    )
    observation_aid: ObservationAidMode = Field(
        default="none",
        description=(
            "Optional information-preserving representation of the manager-visible "
            "observation. 'none' is the native baseline; 'generic_summary' adds a "
            "neutral free-form summary generated only from already-visible evidence."
        ),
    )
    scheduled_worker_disclosures: list[WorkerObservationDisclosure] = Field(
        default_factory=list,
        description=(
            "Manager-facing capability projections and announcements scheduled "
            "independently of objective worker mutations."
        ),
    )

    _capability_overrides: dict[str, list[str]] = PrivateAttr(default_factory=dict)
    _applied_disclosure_timesteps: set[int] = PrivateAttr(default_factory=set)

    async def apply_scheduled_disclosures_for_timestep(
        self,
        timestep: int,
        communication_service: "CommunicationService | None" = None,
    ) -> list[str]:
        """Apply this timestep's manager-facing disclosures exactly once."""
        if timestep in self._applied_disclosure_timesteps:
            return []

        disclosures = [
            disclosure
            for disclosure in self.scheduled_worker_disclosures
            if disclosure.timestep == timestep
        ]
        changes: list[str] = []
        for disclosure in disclosures:
            if disclosure.capability_override is None:
                self._capability_overrides.pop(disclosure.agent_id, None)
                projection = "current canonical capabilities"
            else:
                self._capability_overrides[disclosure.agent_id] = list(
                    disclosure.capability_override
                )
                projection = "an observation-policy capability override"

            if disclosure.announce:
                if not disclosure.announcement:
                    raise ValueError(
                        "An announced worker disclosure requires announcement text."
                    )
                if communication_service is not None:
                    await communication_service.broadcast_message(
                        from_agent=disclosure.agent_id,
                        content=disclosure.announcement,
                    )
            changes.append(
                f"Worker observation disclosure for {disclosure.agent_id}: "
                f"{projection}; announced={disclosure.announce}"
            )

        self._applied_disclosure_timesteps.add(timestep)
        return changes

    def redact_agent_config(self, config):
        """Return a copy of an agent config filtered to this policy."""
        updates: dict = {}
        capability_override = self._capability_overrides.get(config.agent_id)
        if capability_override is not None:
            updates["agent_capabilities"] = list(capability_override)
        if not self.expose_worker_system_prompts:
            updates["system_prompt"] = "[REDACTED]"
        if self.worker_metadata == "id_only":
            updates["agent_description"] = ""
            updates["agent_capabilities"] = []
        return config.model_copy(update=updates) if updates else config
