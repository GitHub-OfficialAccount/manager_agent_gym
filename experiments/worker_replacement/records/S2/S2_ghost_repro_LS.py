"""LS review of S2: does the roster block ghost-repeat after the swap timestep?

Engine per-timestep expression (engine.py:427): set_pending_roster_changes built from
registry._last_applied_changes. If apply_scheduled_changes_for_timestep early-returns on
a quiet timestep WITHOUT resetting the record, the swap lines persist and the manager
sees the announcement forever after.
"""
import asyncio
from manager_agent_gym import AgentRegistry
from manager_agent_gym.schemas.workflow_agents import AIAgentConfig


def cfg(aid):
    return AIAgentConfig(agent_id=aid, agent_type="ai", system_prompt="Capital quant worker.",
                         agent_description="Computes capital.", agent_capabilities=["c"])


async def main():
    r = AgentRegistry()
    r.register_ai_agent(cfg("alpha"), [])
    r.schedule_agent_remove(3, "alpha", "reason-r")
    r.schedule_agent_add(3, cfg("beta"), "reason-a")

    for t in (2, 3, 4, 5):
        await r.apply_scheduled_changes_for_timestep(t)
        engine_expr = [f"{a} {i}" for a, i in getattr(r, "_last_applied_changes", [])]
        print(f"t={t}: engine would pass {engine_expr}")

asyncio.run(main())
