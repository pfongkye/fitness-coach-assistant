from typing import Dict, Any, Optional
from google.adk import Agent
from config.settings import settings
from tools.nutrition_tools import SportsDietitianEngine

def calculate_daily_nutrition_plan(
    gender: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    workout_duration_mins: float = 60.0,
    workout_type: str = "metcon",
    goal: str = "performance"
) -> Dict[str, Any]:
    """
    Calculates BMR, workout caloric expenditure, daily macro breakdown (Protein, Carbs, Fats),
    and baseline hydration based on ISSN sports nutrition guidelines.
    """
    bmr = SportsDietitianEngine.calculate_bmr(
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age
    )
    
    workout_burn = SportsDietitianEngine.calculate_workout_calories(
        weight_kg=weight_kg,
        duration_minutes=workout_duration_mins,
        workout_type=workout_type
    )
    
    macros = SportsDietitianEngine.calculate_daily_macros(
        weight_kg=weight_kg,
        bmr=bmr,
        workout_calories=workout_burn,
        goal=goal
    )
    
    return {
        "bmr_calories": bmr,
        "workout_energy_burn_calories": workout_burn,
        "daily_macro_plan": macros,
        "coaching_advice": f"Fueling for {goal.replace('_', ' ').title()}: Prioritize {macros['protein_g']}g protein evenly across 4 meals and drink at least {macros['hydration_baseline_liters']}L of water."
    }

def recommend_post_workout_recovery_recipes(
    weight_kg: float,
    workout_intensity: str = "high",
    dietary_style: str = "omnivore"
) -> Dict[str, Any]:
    """
    Generates delicious, macro-matched post-workout recovery recipes (Quick Smoothie vs Whole Food Meal)
    tailored to the athlete's dietary preferences (Omnivore, Paleo, Vegan, etc.) and workout intensity.
    """
    return SportsDietitianEngine.generate_post_workout_recipes(
        weight_kg=weight_kg,
        workout_intensity=workout_intensity,
        dietary_style=dietary_style
    )

dietitian_agent = Agent(
    name="dietitian_agent",
    model=settings.fast_model,
    description="Calculates energy expenditure, macronutrient targets, and recommends post-workout recovery recipes and hydration plans.",
    instruction=(
        "You are the Nutrition, Fueling & Sports Dietitian Agent. "
        "Your mission is to prescribe science-backed nutrition to optimize workout recovery and body composition. "
        "Calculate accurate BMR and training burn using ISSN standards. "
        "Always provide practical, delicious post-workout recipe recommendations (both a fast <5-min shake and a whole-food meal) "
        "customized to the athlete's dietary preference (Omnivore, Paleo, Vegan, etc.)."
    ),
    tools=[calculate_daily_nutrition_plan, recommend_post_workout_recovery_recipes]
)
