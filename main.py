import sys
from agents.orchestrator import root_agent
from agents.profile_vault import save_athlete_profile, get_athlete_profile
from agents.adaptive_planner import generate_adapted_workout, conduct_pre_session_checkin
from agents.session_analyst import record_post_session_checkin, get_workout_for_day, get_longitudinal_trends_and_insights
from agents.movement_research import find_movement_technique_and_video
from agents.dietitian import calculate_daily_nutrition_plan, recommend_post_workout_recovery_recipes
from agents.gamification import get_gamification_overview

def run_sample_athlete_journey():
    print("=" * 70)
    print("🏃 AI EXPERT FITNESS COACH ASSISTANT (Powered by Google ADK)")
    print("=" * 70)
    
    user_id = "athlete_pascal"
    
    # 1. Onboarding & Encrypted Profile Storage
    print("\n1. [Profile Vault] Saving encrypted profile...")
    profile_res = save_athlete_profile(
        user_id=user_id,
        age=32,
        gender="male",
        height_cm=180.0,
        weight_kg=80.0,
        city="Paris",
        fitness_level="advanced",
        dietary_preference="paleo",
        injury_history=["minor left shoulder impingement"]
    )
    print(f"-> Encryption Status: {profile_res['status']}")
    print(f"-> Sanitized LLM View: {profile_res['sanitized_profile']}")

    # 2. Pre-Session Check-in & Dynamic Workout Adaptation
    print("\n2. [Adaptive Training Planner] Running Pre-Session Check-in & Weather Adaptation...")
    workout_res = generate_adapted_workout(
        workout_type="High-Intensity Metcon & Squat Strength",
        city_name="Paris",
        energy_level=3,
        sleep_quality="fair",
        soreness_areas=["legs"]
    )
    print(f"-> Pre-Checkin Readiness Score: {workout_res['readiness_summary']['readiness_score']}/100 ({workout_res['readiness_summary']['adaptation_tier']})")
    print(f"-> Localized Weather: {workout_res['localized_weather']['location']} | Temp: {workout_res['localized_weather']['temperature_c']}°C (Heat Index: {workout_res['localized_weather']['heat_index_c']}°C)")
    print(f"-> Applied Adaptations: {workout_res['workout_program'].get('applied_adaptations')}")

    # 3. Movement Research & Verified Video
    print("\n3. [Movement Research] Looking up verified CrossFit mechanics for 'Thruster'...")
    move_res = find_movement_technique_and_video("Thruster")
    print(f"-> Movement: {move_res['movement_name']}")
    print(f"-> Key Points: {move_res['points_of_performance'][:2]}")
    print(f"-> Verified Video Demo: {move_res['official_video_url']}")

    # 4. Post-Session Check-in & History Logging
    print("\n4. [Session Analyst] Submitting Post-Session Check-in...")
    post_res = record_post_session_checkin(
        user_id=user_id,
        rpe=8.5,
        completed_score="13:45 RX",
        movements_performed=["Back Squat", "Thruster", "Pull-Up", "C2 Row"],
        soreness_hotspots=["upper_back", "quads"],
        feedback_notes="Paced thrusters 8-7 unbroken; felt strong despite heat.",
        exercises=[
            {"name": "Back Squat", "weight_kg": 100.0, "sets": 5, "reps": 3},
            {"name": "Thruster", "weight_kg": 43.0, "sets": 4, "reps": 15}
        ]
    )
    print(f"-> Post-Checkin Glycogen Depletion: {post_res['analysis']['glycogen_depletion_level']}")
    print(f"-> Calculated Tonnage: {post_res['saved_session']['calculated_tonnage_kg']} kg")
    print(f"-> Awarded Gamification XP: +{post_res['gamification_reward']['awarded_xp']} XP (Level: {post_res['gamification_reward']['level']})")

    # 5. Dietitian Post-Workout Fueling & Recipes
    print("\n5. [Dietitian Agent] Generating macro refuel and custom Paleo recipes...")
    recipe_res = recommend_post_workout_recovery_recipes(
        weight_kg=80.0,
        workout_intensity="high",
        dietary_style="paleo"
    )
    print(f"-> Target Recovery Macros: {recipe_res['target_recovery_macros']}")
    print(f"-> Quick Shake Option (<5 min): {recipe_res['quick_refuel_option']['title']}")
    print(f"-> Whole Food Meal Option: {recipe_res['whole_food_option']['title']}")

    # 6. Natural Language Date Query ("What did I do today?")
    print("\n6. [History Recall] Querying session history for 'today'...")
    history_res = get_workout_for_day(user_id=user_id, date_query="today")
    print(f"-> Retrieved Session Date: {history_res['session_date']}")
    print(f"-> Movements Logged: {history_res['session']['movements_performed']}")

    # 7. Longitudinal Trends & Movement Balance
    print("\n7. [Longitudinal Trends] Analyzing 30-day training patterns...")
    trend_res = get_longitudinal_trends_and_insights(user_id=user_id, days=30)
    print(f"-> Total Sessions: {trend_res['total_sessions']} | Avg RPE: {trend_res['average_rpe']}/10")
    print(f"-> Insights: {trend_res['coaching_insights']}")

    # 8. Gamification Summary
    print("\n8. [Gamification Overview] Athlete status & Badges...")
    game_res = get_gamification_overview(user_id=user_id)
    print(f"-> Current Level: {game_res['level']} (XP: {game_res['xp']})")
    print(f"-> Current Streak: {game_res['current_streak_days']} days (Freeze Tokens: {game_res['freeze_tokens']})")
    print(f"-> Badges Unlocked: {game_res['badges']}")
    print("=" * 70)
    print("✅ All Multi-Agent Workflows & End-to-End Execution Passed Successfully!")
    print("=" * 70)

if __name__ == "__main__":
    run_sample_athlete_journey()
