"""
Perturbation schedule: controlled mid-episode changes to worker agents.

The injection harness for ad-hoc-teamwork experiments. A schedule is an
executable list of perturbations keyed by timestep, applied through the
AgentRegistry's scheduled-change mechanism (the same machinery as team churn),
plus a ground-truth manifest recording exactly what changed, when, and to
whom — the record that detection/recovery metrics are computed against.

Perturbation kinds currently supported:
- PromptSwap: same agent id, new system prompt (the "type switch" analogue).
- ModelSwap: same agent id, new underlying model (genuine capability change,
  e.g. swapping in a weaker model — degradation that isn't a roleplay the
  model can opt out of).
Both are silent by default: nothing observable changes except subsequent
behavior.

Additional kinds (worker replacement with inherited identity, tool removal,
gradual degradation) will be added as the taxonomy grows.
"""

from typing import TYPE_CHECKING, Annotated, Literal, Union

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ...core.workflow_agents.registry import AgentRegistry


class PromptSwap(BaseModel):
    """Replace a worker's system prompt in place at a given timestep."""

    kind: Literal["prompt_swap"] = "prompt_swap"
    timestep: int = Field(..., ge=0, description="Timestep at which the swap applies")
    agent_id: str = Field(..., description="Worker whose policy changes")
    new_system_prompt: str = Field(..., description="The replacement system prompt")
    announce: bool = Field(
        default=False,
        description="Broadcast the change (announced condition); False = silent",
    )
    label: str = Field(
        default="",
        description="Short experimenter label for this perturbation, e.g. "
        "'competence_degradation'",
    )


class ModelSwap(BaseModel):
    """Replace a worker's underlying model in place at a given timestep."""

    kind: Literal["model_swap"] = "model_swap"
    timestep: int = Field(..., ge=0, description="Timestep at which the swap applies")
    agent_id: str = Field(..., description="Worker whose capability changes")
    new_model_name: str = Field(
        ..., description="The replacement model route (e.g. a weaker model)"
    )
    announce: bool = Field(
        default=False,
        description="Broadcast the change (announced condition); False = silent",
    )
    label: str = Field(
        default="",
        description="Short experimenter label, e.g. 'capability_degradation'",
    )


Perturbation = Annotated[Union[PromptSwap, ModelSwap], Field(discriminator="kind")]


class PerturbationSchedule(BaseModel):
    """An executable, recordable set of perturbations for one run."""

    perturbations: list[Perturbation] = Field(default_factory=list)

    def register(self, agent_registry: "AgentRegistry") -> None:
        """Map every perturbation onto the registry's scheduled changes."""
        for p in self.perturbations:
            if isinstance(p, PromptSwap):
                agent_registry.schedule_prompt_swap(
                    timestep=p.timestep,
                    agent_id=p.agent_id,
                    new_system_prompt=p.new_system_prompt,
                    announce=p.announce,
                    reason=p.label,
                )
            elif isinstance(p, ModelSwap):
                agent_registry.schedule_model_swap(
                    timestep=p.timestep,
                    agent_id=p.agent_id,
                    new_model_name=p.new_model_name,
                    announce=p.announce,
                    reason=p.label,
                )

    def manifest(self) -> dict:
        """Ground-truth record for the run outputs.

        Metrics (time-to-detection, wasted work since changepoint, false-alarm
        rate) are computed by joining behavior streams against this manifest.
        """
        return {
            "num_perturbations": len(self.perturbations),
            "perturbations": [p.model_dump() for p in self.perturbations],
        }
