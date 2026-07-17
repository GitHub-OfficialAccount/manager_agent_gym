"""Manager observability definitions for DS-REROUTE perturbations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from manager_agent_gym.schemas.execution.observation_policy import (
    ObservationPolicy,
    WorkerObservationDisclosure,
)

from .perturbations import (
    MODEL_PROMPT_JUDGMENT,
    TOOLSET_TO_SCREENING,
    Condition,
    PerturbationDefinition,
)
from .scenario import WORKER_SPECS

CapabilityProjection = Literal["baseline", "uncertain", "current"]


@dataclass(frozen=True)
class ObservabilityDefinition:
    """One condition's projection of an otherwise identical worker mutation."""

    condition: Condition
    capability_projection: CapabilityProjection
    announce: bool
    announcement_detail: Literal["none", "generic", "specific"]

    def manifest(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DisclosureProfile:
    baseline_capabilities: tuple[str, ...] | None
    uncertain_capabilities: tuple[str, ...] | None
    current_capabilities: tuple[str, ...] | None
    generic_announcement: str
    specific_announcement: str


OBSERVABILITY_DEFINITIONS: dict[Condition, ObservabilityDefinition] = {
    "control": ObservabilityDefinition("control", "baseline", False, "none"),
    "silent": ObservabilityDefinition("silent", "baseline", False, "none"),
    "partial": ObservabilityDefinition("partial", "uncertain", True, "generic"),
    "full": ObservabilityDefinition("full", "current", True, "specific"),
}

DISCLOSURE_PROFILES: dict[str, DisclosureProfile] = {
    TOOLSET_TO_SCREENING: DisclosureProfile(
        baseline_capabilities=tuple(WORKER_SPECS["portfolio_analyst"][1]),
        uncertain_capabilities=(
            "Methods: changed; current outlier-screening method unknown",
            "Methods: portfolio profiling",
        ),
        current_capabilities=tuple(WORKER_SPECS["screening_analyst"][1]),
        generic_announcement="The analyst's capability profile changed.",
        specific_announcement=(
            "The analyst's robust percentile analysis changed to "
            "mean-plus-two-SD screening."
        ),
    ),
    MODEL_PROMPT_JUDGMENT: DisclosureProfile(
        baseline_capabilities=None,
        uncertain_capabilities=None,
        current_capabilities=None,
        generic_announcement="The analyst's behavior changed.",
        specific_announcement=(
            "The analyst's model and analytical judgment changed; it now has "
            "limited multi-part integration ability."
        ),
    ),
}


def get_observability(condition: Condition) -> ObservabilityDefinition:
    return OBSERVABILITY_DEFINITIONS[condition]


def build_observation_policy(
    condition: Condition,
    perturbation: PerturbationDefinition,
    swap_timestep: int,
    observation_aid: str = "none",
) -> ObservationPolicy:
    """Compose a condition with a perturbation without changing the mutation."""
    observability = get_observability(condition)
    disclosures: list[WorkerObservationDisclosure] = []
    if condition != "control":
        profile = DISCLOSURE_PROFILES[perturbation.name]
        capabilities = {
            "baseline": profile.baseline_capabilities,
            "uncertain": profile.uncertain_capabilities,
            "current": profile.current_capabilities,
        }[observability.capability_projection]
        announcement = {
            "none": None,
            "generic": profile.generic_announcement,
            "specific": profile.specific_announcement,
        }[observability.announcement_detail]
        disclosures.append(
            WorkerObservationDisclosure(
                timestep=swap_timestep,
                agent_id=perturbation.target_worker,
                capability_override=list(capabilities) if capabilities else None,
                announce=observability.announce,
                announcement=announcement,
            )
        )

    return ObservationPolicy(
        expose_worker_system_prompts=False,
        worker_metadata="capabilities",
        quality_digest="none",
        observation_aid=observation_aid,
        scheduled_worker_disclosures=disclosures,
    )
