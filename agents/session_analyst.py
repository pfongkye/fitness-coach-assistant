from typing import Dict, Any, List, Optional
from google.adk import Agent
from config.settings import settings
from tools.readiness_tools import ReadinessEngine, PostSessionCheckin
from tools.history_tools import workout_history_ledger
from mcp_servers.gamification_engine import gamification_service

def record_post_session_checkin(
    user_id: str,
    rpe: float,
    completed_score: str,
    movements_performed: List[str],
    soreness_hotspots: Optional[List[str]] = None,
    acute_joint_pain: bool = False,
    feedback_notes: str = "",
    estimated_duration_mins: int = 45,
    exercises: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Evaluates completed workout performance with a post-session check-in (RPE 1-10, soreness, joint pain),
    commits the session to the historical ledger, and awards gamification XP.
    """
    # 1. Post check-in analysis
    checkin = PostSessionCheckin(
        rpe=rpe,
        completed_score=completed_score,
        soreness_hotspots=soreness_hotspots or [],
        acute_joint_pain=acute_joint_pain,
        feedback_notes=feedback_notes
    )
    analysis = ReadinessEngine.evaluate_post_session(checkin)
    
    # 2. Commit to historical ledger
    session_record = {
        "user_id": user_id,
        "completed_score": completed_score,
        "rpe": rpe,
        "duration_minutes": estimated_duration_mins,
        "movements_performed": movements_performed,
        "exercises": exercises or [],
        "soreness_hotspots": soreness_hotspots or [],
        "feedback_notes": feedback_notes,
        "acute_joint_pain": acute_joint_pain
    }
    logged_record = workout_history_ledger.log_session(user_id, session_record)
    
    # 3. Award XP & Gamification
    xp_award = gamification_service.award_xp(
        user_id=user_id,
        xp_amount=settings.xp_per_workout + settings.xp_per_post_checkin,
        activity_label=f"Workout Logged ({completed_score})"
    )
    
    return {
        "analysis": analysis,
        "saved_session": logged_record,
        "gamification_reward": xp_award
    }

def get_workout_for_day(user_id: str, date_query: str) -> Dict[str, Any]:
    """
    Retrieves a past workout session by date query (e.g. 'last Tuesday', 'yesterday', '2026-08-15', 'today').
    """
    record = workout_history_ledger.get_session_by_date(user_id, date_query)
    if record:
        return {
            "found": True,
            "query": date_query,
            "session_date": record.get("date"),
            "session": record
        }
    return {
        "found": False,
        "query": date_query,
        "message": f"No workout found for '{date_query}'. You can check recent history or log a new workout!"
    }

def get_longitudinal_trends_and_insights(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Computes accumulated tonnage (volume), average RPE, workout frequency, and movement pattern balance
    over the specified time window (e.g. 30 days).
    """
    return workout_history_ledger.calculate_longitudinal_trends(user_id=user_id, days=days)

session_analyst_agent = Agent(
    name="session_analyst_agent",
    model=settings.fast_model,
    description="Evaluates completed workout sessions, logs them to history, answers date-based workout queries, and analyzes training volume/RPE trends.",
    instruction=(
        "You are the Session, Trends & History Analyst Agent. "
        "Your role is to evaluate completed workouts via post-session check-ins (RPE, muscular fatigue, pain screeners), "
        "save workouts to the history ledger, retrieve past workouts when the athlete asks for a specific day ('What did I do last Tuesday?'), "
        "and provide longitudinal training insights and movement balance alerts."
    ),
    tools=[record_post_session_checkin, get_workout_for_day, get_longitudinal_trends_and_insights]
)
