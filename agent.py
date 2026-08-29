"""
Entrypoint for Google Agent Development Kit (ADK).
Exposes the root_agent for 'adk web', 'adk run', and 'adk deploy cloud_run'.
"""
from agents.orchestrator import root_agent

# ADK entrypoint
__all__ = ["root_agent"]

if __name__ == "__main__":
    import asyncio
    print(f"Loaded ADK Root Agent: {root_agent.name}")
    print(f"Configured Model: {root_agent.model}")
    print(f"Sub-agents: {[sa.name for sa in root_agent.sub_agents]}")
