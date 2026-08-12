"""Verify observation_source records BOTH branches distinguishably (RR round-2 item 1)."""
import asyncio, sys
sys.path.insert(0, 'tests')
from uuid import uuid4
from helpers.stubs import ManagerNoOp
from manager_agent_gym.core.execution.engine import WorkflowExecutionEngine
from manager_agent_gym.core.workflow_agents.registry import AgentRegistry
from manager_agent_gym.core.communication.service import CommunicationService
from manager_agent_gym.core.common.run_trace import RunTraceRecorder
from manager_agent_gym.core.manager_agent.interface import ManagerAgent
from manager_agent_gym.schemas.core.workflow import Workflow
from manager_agent_gym.schemas.execution.manager_actions import NoOpAction
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from examples.common_stakeholders import create_stakeholder_agent


class CapturingManager(ManagerAgent):
    """Captures its own decision observation, as the structured manager does —
    exercising the "manager" branch without an LLM call."""

    def __init__(self):
        super().__init__(agent_id="capturing", preferences=PreferenceWeights(preferences=[]))

    async def step(self, **kwargs):
        obs = await self.create_observation(
            workflow=kwargs["workflow"],
            execution_state=kwargs["execution_state"],
            current_timestep=kwargs["current_timestep"],
            running_tasks=kwargs["running_tasks"],
            completed_task_ids=kwargs["completed_task_ids"],
            failed_task_ids=kwargs["failed_task_ids"],
            communication_service=kwargs.get("communication_service"),
            stakeholder_profile=kwargs["stakeholder_profile"],
        )
        self.capture_decision_observation(obs)
        return NoOpAction(reasoning="probe")

    async def take_action(self, observation):
        return NoOpAction(reasoning="probe")

    def reset(self) -> None:
        pass


def cfg(i):
    return AIAgentConfig(agent_id=i, agent_type="ai",
                         system_prompt="You are a capital quant worker.",
                         agent_description="Computes capital.",
                         agent_capabilities=["Computes RWA"])


async def probe(manager, label):
    reg = AgentRegistry()
    reg.schedule_agent_add(0, cfg("newcomer"), "joins the engagement")
    rec = RunTraceRecorder(metadata={"probe": label})
    eng = WorkflowExecutionEngine(
        workflow=Workflow(name="t", workflow_goal="goal", owner_id=uuid4()),
        agent_registry=reg,
        stakeholder_agent=create_stakeholder_agent(
            persona="balanced", preferences=PreferenceWeights(preferences=[])),
        manager_agent=manager, communication_service=CommunicationService(),
        max_timesteps=1, seed=42,
        enable_timestep_logging=False, enable_final_metrics_logging=False)
    with rec.activate():
        try:
            await eng.execute_timestep()
        except Exception as exc:
            print(f"  {label}: engine raised {type(exc).__name__}")
    for e in rec.events:
        if e.get("event_type") == "roster_arrival_announced":
            p = e["payload"]
            print(f"  {label:<22} observation_source={p['observation_source']!r:<18} "
                  f"rendered={p['rendered_into_observation']}  {p['applied_changes']}")
            return p["observation_source"]
    print(f"  {label}: NO EVENT")
    return None


async def main():
    print("S2 RR round-2 item 1 — observation_source distinguishes the two branches\n")
    a = await probe(CapturingManager(), "captures own obs")
    b = await probe(ManagerNoOp(), "relies on fallback")
    ok = a == "manager" and b == "engine_fallback"
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — branches distinguishable in the log "
          f"({a!r} vs {b!r})")
    return 0 if ok else 1

raise SystemExit(asyncio.run(main()))
