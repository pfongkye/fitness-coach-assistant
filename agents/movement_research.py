from typing import Dict, Any, List
from google.adk import Agent
from config.settings import settings
from mcp_servers.crossfit_knowledge import CrossFitKnowledgeService

crossfit_kb = CrossFitKnowledgeService()

def find_movement_technique_and_video(movement_name: str) -> Dict[str, Any]:
    """
    Searches for official CrossFit movement standards, points of performance,
    common faults, and verified YouTube video demo links.
    """
    movement = crossfit_kb.search_movement(movement_name)
    if movement:
        return {
            "found": True,
            "movement_name": movement["name"],
            "category": movement.get("category"),
            "points_of_performance": movement.get("points_of_performance", []),
            "common_faults": movement.get("common_faults", []),
            "scaling_options": movement.get("scaling_options", []),
            "official_video_url": movement.get("official_video_url", ""),
            "source": movement.get("source", "CrossFit Training")
        }
    return {
        "found": False,
        "movement_name": movement_name,
        "message": f"Movement '{movement_name}' not found in standard seed database.",
        "fallback_video_source": f"https://www.youtube.com/results?search_query=CrossFit+{movement_name.replace(' ', '+')}+movement+demo"
    }

def get_scaling_ladder(movement_name: str) -> Dict[str, Any]:
    """
    Provides progressive scaling options and modifications for high-skill or heavy movements
    (e.g., Pull-ups, Muscle-ups, Handstand Pushups, Snatches).
    """
    return crossfit_kb.get_scaling_guide(movement_name)

def list_official_crossfit_movements() -> List[str]:
    """Lists all cataloged CrossFit foundational, Olympic, and Gymnastics movements."""
    return crossfit_kb.list_all_movements()

movement_research_agent = Agent(
    name="movement_research_agent",
    model=settings.fast_model,
    description="Provides verified CrossFit movement standards, setup cues, points of performance, common faults, and official video demos.",
    instruction=(
        "You are the Movement and Technique Research Agent. "
        "Your mission is to teach proper movement mechanics using official CrossFit standards. "
        "Always provide clear points of performance, highlight common faults, offer scaling options, "
        "and provide the official video URL for visual guidance."
    ),
    tools=[find_movement_technique_and_video, get_scaling_ladder, list_official_crossfit_movements]
)
