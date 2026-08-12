"""S8 — what does the manager OBSERVE when a capacity-bound worker declines?

Answers the question LS raised on the obligation-2 ruling: when
CapacityBoundedAIAgent refuses a fourth segment, what does the manager see, and is
that observation capacity-shaped only — no coverage leak through the decline?

ZERO API CALLS. A post-swap worker is deliberately over-assigned four segment
tasks against a cap of three; the fourth must be declined. The manager's
observation for the declined task is then dumped verbatim rather than described.

  uv run python -m experiments.worker_replacement.records.S8.S8_decline_probe

Output committed beside this file as S8_decline_probe_output.txt.
"""
import asyncio, json
from uuid import UUID, uuid4

from manager_agent_gym.core.execution.engine import WorkflowExecutionEngine
from manager_agent_gym.core.manager_agent import structured_manager
from manager_agent_gym.core.workflow_agents import ai_agent as ai_agent_module
from manager_agent_gym.core.workflow_agents.stakeholder_agent import StakeholderAgent
from manager_agent_gym.schemas.core.base import TaskStatus
from manager_agent_gym.schemas.core.resources import Resource
from manager_agent_gym.schemas.execution.manager_actions import NoOpAction
from manager_agent_gym.schemas.preferences.preference import PreferenceWeights
from manager_agent_gym.schemas.unified_results import create_task_result
from manager_agent_gym.schemas.workflow_agents.stakeholder import StakeholderConfig

from experiments.worker_replacement import finance_env as env

async def _stub_execute(self, task, resources):
    return create_task_result(
        task_id=task.id, agent_id=self.config.agent_id, success=True,
        execution_time=0.01,
        resources=[Resource(name=f"{task.name} out", description="stub",
                            content="method: SA\nrwa: 1000.00")])
ai_agent_module.AIAgent.execute_task = _stub_execute

captured = {}

async def _stub_take_action(self, observation):
    captured.setdefault("observations", []).append(observation)
    return NoOpAction(reasoning="probe")
structured_manager.ChainOfThoughtManagerAgent.take_action = _stub_take_action

built = env.build_environment(101)
workflow, index = built["workflow"], built["index"]
event = built["instance"]["event"]

# Pre-assign the FIRST FOUR segment tasks to ONE post-swap worker: three will run,
# the fourth must be declined by the capacity bound.
victim = event["roster_post_swap"][1]
seg_ids = list(index["segment_task_ids"].values())
over = seg_ids[:4]
for tid in over:
    workflow.tasks[UUID(tid)].assigned_agent_id = victim
for tid in index["fixed_task_ids"]:
    workflow.tasks[UUID(tid)].assigned_agent_id = event["predecessor_id"]

manager = structured_manager.ChainOfThoughtManagerAgent(
    preferences=PreferenceWeights(preferences=[]), model_name="none")
stakeholder = StakeholderAgent(config=StakeholderConfig(
    agent_id="stakeholder", agent_type="stakeholder",
    system_prompt="stakeholder for the decline probe", model_name="none",
    agent_description="stakeholder for the decline probe",
    agent_capabilities=["stakeholder"], name="S", role="Owner",
    initial_preferences=PreferenceWeights(preferences=[])))

engine = WorkflowExecutionEngine(
    workflow=workflow, agent_registry=built["registry"], manager_agent=manager,
    stakeholder_agent=stakeholder, max_timesteps=built["horizon"],
    enable_timestep_logging=False, enable_final_metrics_logging=False, seed=1)

asyncio.run(engine.run_full_execution(save_outputs=False))

declined = over[3]
task = workflow.tasks[UUID(declined)]
print("=" * 72)
print("OVER-ASSIGNED WORKER:", victim, "| segment tasks pinned to it: 4, cap 3")
counts = {}
for tid in over:
    t = workflow.tasks[UUID(tid)]
    counts[t.name] = t.status.value
print("their statuses:", json.dumps(counts, indent=2))
print()
print("THE DECLINED TASK, exactly as the manager's summary renders it:")
print(task.pretty_print(indent=1))
print()
last = captured["observations"][-1]
print("assigned_agent_id present in the rendered task text? ",
      victim in task.pretty_print())
print("declined task in observation.ready_task_ids? ",
      UUID(declined) in last.ready_task_ids)
print("declined task in observation.running_task_ids?",
      UUID(declined) in last.running_task_ids)
print("declined task in observation.failed_task_ids? ",
      UUID(declined) in last.failed_task_ids)
print()
blob = json.dumps({
    "summary": last.workflow_summary,
    "messages": [m.content for m in last.recent_messages],
    "roster": last.roster_changes,
}, default=str)
for token in ["capacity", "decline", "declin", "at capacity", "max_concurrent",
              "full", "cap "]:
    print(f"  observation mentions {token!r}: {token.lower() in blob.lower()}")
print()
print("coverage-leak check — does any observation text name the victim's "
      "irb_coverage classes?")
worker = next(w for w in built["instance"]["workers"] if w["worker_id"] == victim)
for cls in worker["irb_coverage"]:
    # asset classes DO legitimately appear in task text; the question is whether
    # the DECLINE adds any linkage between the worker and a class.
    print(f"  class {cls!r} appears in the declined task's own text: "
          f"{cls in task.pretty_print()}")
