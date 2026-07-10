"""
🚀 Hello Manager Agent

This example demonstrates the absolute basics of the Manager Agent Gym library:
1. Creating a simple workflow with tasks
2. Setting up a manager agent with preferences
3. Running the execution engine and seeing results

This is your "Hello World" for autonomous workflow management!
"""

import asyncio

# Import key components from manager_agent_gym
# Many components are available at the top level for convenience
from examples.end_to_end_examples.icap.workflow import create_workflow
from manager_agent_gym import (
    ChainOfThoughtManagerAgent,
    WorkflowExecutionEngine,
    AgentRegistry,
    PreferenceWeights,
    Preference,
)
from manager_agent_gym.schemas.preferences.evaluator import (
    Evaluator,
    AggregationStrategy,
)
from examples.common_stakeholders import create_stakeholder_agent


def create_basic_preferences() -> PreferenceWeights:
    """Create simple preferences focused on quality and reasonable timelines."""
    return PreferenceWeights(
        preferences=[
            Preference(
                name="quality",
                weight=0.4,
                description="High-quality deliverables",
                evaluator=Evaluator(
                    name="quality_eval",
                    description="placeholder",
                    aggregation=AggregationStrategy.WEIGHTED_AVERAGE,
                    rubrics=[],
                ),
            ),
            Preference(
                name="time",
                weight=0.3,
                description="Reasonable timeline",
                evaluator=Evaluator(
                    name="time_eval",
                    description="placeholder",
                    aggregation=AggregationStrategy.WEIGHTED_AVERAGE,
                    rubrics=[],
                ),
            ),
            Preference(
                name="cost",
                weight=0.2,
                description="Cost-effective execution",
                evaluator=Evaluator(
                    name="cost_eval",
                    description="placeholder",
                    aggregation=AggregationStrategy.WEIGHTED_AVERAGE,
                    rubrics=[],
                ),
            ),
            Preference(
                name="oversight",
                weight=0.1,
                description="Manageable oversight",
                evaluator=Evaluator(
                    name="oversight_eval",
                    description="placeholder",
                    aggregation=AggregationStrategy.WEIGHTED_AVERAGE,
                    rubrics=[],
                ),
            ),
        ]
    )


async def run_hello_manager_agent():
    """
    🎯 The Complete Hello World Example

    This function shows you exactly how to:
    - Create a workflow
    - Set up a manager agent
    - Run the execution
    - See what happens
    """

    # Step 1: Create a simple workflow
    # This gives us a toy workflow with ~3-5 research tasks
    print("📋 Creating workflow...")
    workflow = create_workflow()
    print(f"✅ Created workflow '{workflow.name}' with {len(workflow.tasks)} tasks")

    # Step 2: Set up an agent registry with the workflow's agents
    print("\n👥 Setting up agent registry...")
    agent_registry = AgentRegistry()
    # workflow.agents is a dict[str, agent], so we iterate over the values
    for agent in workflow.agents.values():
        agent_registry.register_agent(agent)
    print(f"✅ Registered {len(workflow.agents)} agents")

    # Step 3: Create a manager agent with preferences
    print("\n🧠 Creating manager agent...")
    preferences = create_basic_preferences()
    manager = ChainOfThoughtManagerAgent(
        preferences=preferences,
        manager_persona="Organized Project Coordinator",
    )
    print("✅ Manager agent created with quality-focused preferences")

    # Step 4: Set up the execution engine
    print("\n🚀 Setting up execution engine...")
    stakeholder = create_stakeholder_agent(persona="balanced", preferences=preferences)
    engine = WorkflowExecutionEngine(
        workflow=workflow,
        agent_registry=agent_registry,
        manager_agent=manager,
        stakeholder_agent=stakeholder,
        max_timesteps=20,  # Limited for demo
        enable_timestep_logging=True,
        seed=42,
    )
    print("✅ Execution engine ready")

    # Step 5: Run the workflow!
    print("\n🎬 Starting workflow execution...")
    print("=" * 60)

    try:
        timestep_results = await engine.run_full_execution()

        # Step 6: Show what happened
        print("\n" + "=" * 60)
        print("🎉 EXECUTION COMPLETE!")
        print("=" * 60)

        print("\n📊 SUMMARY:")
        print(f"• Total timesteps: {len(timestep_results)}")
        print(f"• Tasks completed: {len(engine.completed_task_ids)}")
        print(f"• Tasks total: {len(workflow.tasks)}")

        completion_rate = len(engine.completed_task_ids) / len(workflow.tasks) * 100
        print(f"• Completion rate: {completion_rate:.1f}%")
        print(f"• Final execution state: {engine.execution_state}")

        print("\n🧠 MANAGER ACTIONS TAKEN:")
        action_counts = {}
        for timestep_result in timestep_results:
            if "manager_action" in timestep_result.metadata:
                action_data = timestep_result.metadata["manager_action"]
                action_type = action_data.get("action_type", "Unknown")
                action_counts[action_type] = action_counts.get(action_type, 0) + 1

        for action_type, count in action_counts.items():
            print(f"• {action_type}: {count} times")

        print("\n💯 WORKFLOW STATUS:")
        print(f"• Workflow completed: {workflow.is_complete()}")
        print(f"• Failed tasks: {len(engine.failed_task_ids)}")

        if completion_rate == 100:
            print("\n🎊 SUCCESS: All tasks completed!")
        else:
            print(f"\n📈 PROGRESS: {completion_rate:.1f}% of workflow completed")

    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        raise


def main():
    """
    🎯 Main Entry Point

    Run this function to see the Manager Agent Gym in action!
    """
    print("🚀 Welcome to Manager Agent Gym!")
    print("This demo shows the core workflow execution cycle.\n")

    asyncio.run(run_hello_manager_agent())

    print("\n✨ Demo complete! You've just seen:")
    print("• How to create workflows with the WorkflowBuilder")
    print("• How to configure manager agents with preferences")
    print("• How the execution engine orchestrates everything")
    print("• How managers observe state and take actions")
    print("\n🎯 Next: Try the agent communication example!")


if __name__ == "__main__":
    main()
