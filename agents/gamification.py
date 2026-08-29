from typing import Dict, Any
from google.adk import Agent
from config.settings import settings
from mcp_servers.gamification_engine import gamification_service

def award_xp_to_athlete(user_id: str, xp_amount: int, activity_label: str) -> Dict[str, Any]:
    """Awards experience points (XP) to the athlete, checks for level-ups, and updates streaks."""
    return gamification_service.award_xp(user_id=user_id, xp_amount=xp_amount, activity_label=activity_label)

def record_personal_record(user_id: str, movement: str, value: str) -> Dict[str, Any]:
    """Logs a new Personal Record (PR), unlocks a milestone badge, and awards 150 bonus XP."""
    return gamification_service.log_pr(user_id=user_id, movement=movement, value=value)

def get_gamification_overview(user_id: str) -> Dict[str, Any]:
    """Retrieves the athlete's current level, total XP, streaks, streak freeze tokens, badges, and active quests."""
    return gamification_service.get_profile_summary(user_id=user_id)

gamification_agent = Agent(
    name="gamification_agent",
    model=settings.fast_model,
    description="Manages athlete motivation, XP leveling, streak tracking with Freeze Tokens, PR badges, and weekly quests.",
    instruction=(
        "You are the Motivation & Gamification Agent. "
        "Your mission is to keep the athlete motivated, celebrating PRs, awarding XP, tracking streaks, "
        "and managing quests using positive behavioral reinforcement."
    ),
    tools=[award_xp_to_athlete, record_personal_record, get_gamification_overview]
)
