import pytest
from tools.nutrition_tools import SportsDietitianEngine

def test_bmr_calculation():
    # Male: 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    bmr_male = SportsDietitianEngine.calculate_bmr("male", 80.0, 180.0, 30)
    assert bmr_male == 1780.0

    # Female: 10*60 + 6.25*165 - 5*28 - 161 = 600 + 1031.25 - 140 - 161 = 1330.25 -> 1330.2
    bmr_female = SportsDietitianEngine.calculate_bmr("female", 60.0, 165.0, 28)
    assert abs(bmr_female - 1330.2) <= 0.1

def test_workout_calories_calculation():
    # Metcon: 10.5 MET * 80kg * (60/60) = 840 cals
    burn = SportsDietitianEngine.calculate_workout_calories(80.0, 60.0, "metcon")
    assert burn == 840.0

def test_macro_breakdown():
    macros = SportsDietitianEngine.calculate_daily_macros(
        weight_kg=80.0,
        bmr=1780.0,
        workout_calories=600.0,
        goal="performance"
    )
    assert macros["target_calories"] > 2500
    assert macros["protein_g"] == round(80.0 * 1.9, 1)
    assert macros["fat_g"] == round(80.0 * 0.9, 1)
    assert macros["carbohydrates_g"] > 200

def test_post_workout_recipes_generation():
    recipes = SportsDietitianEngine.generate_post_workout_recipes(
        weight_kg=80.0,
        workout_intensity="high",
        dietary_style="paleo"
    )
    assert recipes["dietary_style"] == "Paleo"
    assert "quick_refuel_option" in recipes
    assert "whole_food_option" in recipes
    assert len(recipes["quick_refuel_option"]["ingredients"]) > 0
    assert recipes["target_recovery_macros"]["protein_grams"] == 32.0
