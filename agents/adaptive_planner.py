from typing import Dict, Any, List, Optional
from google.adk import Agent
from config.settings import settings
from tools.readiness_tools import ReadinessEngine, PreSessionCheckin
from tools.periodization_tools import PeriodizationEngine
from mcp_servers.weather_service import WeatherAdaptationService
from mcp_servers.crossfit_knowledge import CrossFitKnowledgeService
from agents.profile_vault import check_profile_completeness

crossfit_kb = CrossFitKnowledgeService()

def conduct_pre_session_checkin(
    user_id: str = "default_user",
    energy_level: int = 3,
    sleep_quality: str = "good",
    soreness_areas: Optional[List[str]] = None,
    soreness_severity: int = 3,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Evaluates the athlete's pre-session readiness before a workout based on energy (1-5),
    sleep quality ('poor', 'fair', 'good', 'excellent'), and soreness areas.
    Also checks profile completeness for missing biometrics (gender, age, height, weight,
    weekly training frequency, and CrossFit experience).
    """
    profile_check = check_profile_completeness(user_id)
    
    checkin = PreSessionCheckin(
        energy_level=energy_level,
        sleep_quality=sleep_quality,
        soreness_areas=soreness_areas or [],
        soreness_severity=soreness_severity,
        notes=notes
    )
    readiness_eval = ReadinessEngine.evaluate_pre_session(checkin)
    
    return {
        "readiness": readiness_eval,
        "profile_status": profile_check,
        "needs_profile_onboarding": not profile_check.get("is_complete", False),
        "onboarding_prompt": profile_check.get("prompt_message") if not profile_check.get("is_complete", False) else None
    }

def check_localized_weather(city_name: str) -> Dict[str, Any]:
    """
    Checks localized real-time weather, heat index, and rain at the athlete's city
    to evaluate environmental training safety and indoor/outdoor adaptations.
    """
    return WeatherAdaptationService.get_weather_by_city(city_name)

def generate_adapted_workout(
    workout_type: str,
    city_name: str,
    user_id: str = "default_user",
    energy_level: int = 4,
    sleep_quality: str = "good",
    soreness_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates a periodized workout and dynamically adapts movements, loads, and outdoor components
    based on localized weather and the athlete's pre-session check-in readiness.
    If the athlete's profile is incomplete, prompts for missing baseline metrics without guessing.
    """
    # 1. Evaluate Readiness & Profile
    checkin_data = conduct_pre_session_checkin(
        user_id=user_id,
        energy_level=energy_level,
        sleep_quality=sleep_quality,
        soreness_areas=soreness_areas or []
    )
    
    # 2. Evaluate Weather
    weather = check_localized_weather(city_name)
    
    # 3. Base Workout Template
    base_workout = {
        "title": f"Daily Workout: {workout_type.title()}",
        "warm_up": "3 Rounds: 10 Pass-Throughs, 10 Air Squats, 5 Inchworms, 200m Easy Jog or Row",
        "strength_portion": "5 Sets of 3 Back Squats @ 75-80% 1RM (Rest 2 min)",
        "metcon_portion": "For Time: 4 Rounds of 400m Run + 15 Thrusters (43/30 kg) + 12 Pull-ups",
        "stimulus_target": "Maintain unbroken thruster sets; target pace 12-15 minutes"
    }
    
    # 4. Adapt workout
    adapted_workout = PeriodizationEngine.adapt_workout_for_conditions(
        base_workout=base_workout,
        readiness_data=checkin_data["readiness"],
        weather_data=weather
    )
    
    return {
        "readiness_summary": checkin_data["readiness"],
        "profile_completeness": checkin_data["profile_status"],
        "localized_weather": weather,
        "workout_program": adapted_workout,
        "coach_note": "Profile is complete." if checkin_data["profile_status"].get("is_complete") else checkin_data["profile_status"].get("prompt_message")
    }

def get_benchmark_wod_details(benchmark_name: str) -> Dict[str, Any]:
    """Retrieves official CrossFit benchmark workout details (e.g., Fran, Cindy, Murph, Helen, Grace)."""
    wod = crossfit_kb.get_benchmark_wod(benchmark_name)
    if wod:
        return {"found": True, "wod": wod}
    return {"found": False, "message": f"Benchmark '{benchmark_name}' not found in local library."}

adaptive_planner_agent = Agent(
    name="adaptive_planner_agent",
    model=settings.fast_model,
    description="Plans periodized CrossFit & athletic workouts and dynamically adapts them to localized weather and pre-session fatigue.",
    instruction=(
        "You are the Adaptive Training Planner Agent. "
        "Your mission is to prescribe smart, periodized training and adapt sessions dynamically. "
        "Always execute a pre-session check-in (energy, sleep, soreness) and check localized weather. "
        "CRITICAL RULE: NEVER guess or assume biometric values (gender, age, height, weight, weekly training frequency, or CrossFit experience duration). "
        "If check_profile_completeness indicates missing information, politely ask the user for these specific details before finalizing customized weights and progressions. "
        "If heat is extreme (>=32°C) or it is raining, adapt outdoor running to indoor Concept2 rowing or Echo bikes. "
        "If the athlete is fatigued or sore, scale volume or swap exercises to protect joints and ensure progress."
    ),
    tools=[conduct_pre_session_checkin, check_localized_weather, generate_adapted_workout, get_benchmark_wod_details, check_profile_completeness]
)
