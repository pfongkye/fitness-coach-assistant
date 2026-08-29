from typing import Dict, Any, List, Optional

class SportsDietitianEngine:
    """Computes evidence-based sports nutrition plans and post-workout recipes."""

    @staticmethod
    def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
        """Mifflin-St Jeor formula for Basal Metabolic Rate."""
        s = +5 if gender.lower() in ["male", "m", "man"] else -161
        bmr = 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + s
        return round(bmr, 1)

    @staticmethod
    def calculate_workout_calories(weight_kg: float, duration_minutes: float, workout_type: str = "metcon") -> float:
        """Computes workout energy expenditure using METs (Metabolic Equivalent of Task)."""
        met_map = {
            "metcon": 10.5,
            "crossfit": 10.0,
            "heavy_strength": 6.0,
            "olympic_lifting": 5.5,
            "aerobic_zone2": 7.0,
            "mobility_recovery": 2.5
        }
        met = met_map.get(workout_type.lower(), 8.0)
        # Calories = MET * weight_kg * (duration_hours)
        calories = met * weight_kg * (duration_minutes / 60.0)
        return round(calories, 1)

    @staticmethod
    def calculate_daily_macros(
        weight_kg: float,
        bmr: float,
        workout_calories: float,
        goal: str = "performance",
        activity_multiplier: float = 1.35
    ) -> Dict[str, Any]:
        """
        Calculates daily energy budget and macronutrient split according to ISSN guidelines.
        Goals: 'performance', 'fat_loss', 'muscle_gain', 'maintenance'
        """
        base_tdee = bmr * activity_multiplier + workout_calories
        
        if goal == "fat_loss":
            target_calories = max(1500.0, base_tdee - 400.0)
            protein_g_per_kg = 2.2  # Higher protein to preserve lean mass in deficit
        elif goal == "muscle_gain":
            target_calories = base_tdee + 350.0
            protein_g_per_kg = 2.0
        else:  # performance / maintenance
            target_calories = base_tdee
            protein_g_per_kg = 1.9

        protein_g = round(weight_kg * protein_g_per_kg, 1)
        protein_cals = protein_g * 4.0
        
        # Dietary fat: 0.9 g/kg for hormone regulation
        fat_g = round(weight_kg * 0.9, 1)
        fat_cals = fat_g * 9.0
        
        # Remaining calories to carbohydrates
        remaining_cals = max(0.0, target_calories - protein_cals - fat_cals)
        carbs_g = round(remaining_cals / 4.0, 1)
        
        return {
            "target_calories": round(target_calories, 0),
            "protein_g": protein_g,
            "carbohydrates_g": carbs_g,
            "fat_g": fat_g,
            "protein_calories": round(protein_cals, 0),
            "carbs_calories": round(remaining_cals, 0),
            "fat_calories": round(fat_cals, 0),
            "hydration_baseline_liters": round(weight_kg * 0.035 + (workout_calories / 1000.0) * 0.75, 2)
        }

    @staticmethod
    def generate_post_workout_recipes(
        weight_kg: float,
        workout_intensity: str = "high",
        dietary_style: str = "omnivore"
    ) -> Dict[str, Any]:
        """
        Generates macro-matched post-workout recovery recipes (Quick Smoothie vs Whole Food Meal)
        tailored to dietary restrictions (Paleo, Vegan, Omnivore, etc.).
        """
        # Post-workout target: ~0.4g/kg protein and ~0.8g/kg fast carbohydrates
        target_protein = round(weight_kg * 0.4, 0)
        target_carbs = round(weight_kg * (0.8 if workout_intensity == "high" else 0.5), 0)
        
        diet_lower = dietary_style.lower()
        
        # Recipe Database by Dietary Style
        recipe_catalog = {
            "omnivore": {
                "quick_shake": {
                    "title": "Berry-Blast Glycogen Refuel Smoothie",
                    "prep_time_minutes": 3,
                    "target_macros": {"protein_g": target_protein, "carbs_g": target_carbs, "fat_g": 6},
                    "ingredients": [
                        f"{int(target_protein // 25)} scoop(s) Whey Isolate Protein (approx {int(target_protein)}g protein)",
                        "1 ripe large banana (fast glucose replenishment)",
                        "1 cup frozen mixed berries (blueberries/cherries for anti-inflammatory polyphenols)",
                        "300ml cold coconut water (natural potassium & electrolytes)",
                        "1 tbsp raw honey",
                        "1 pinch Celtic sea salt (replaces lost sodium)"
                    ],
                    "instructions": "Blend all ingredients on high for 45 seconds until smooth. Drink within 45 minutes of training."
                },
                "whole_food_meal": {
                    "title": "Honey-Dijon Chicken & Roasted Sweet Potato Power Bowl",
                    "prep_time_minutes": 20,
                    "target_macros": {"protein_g": target_protein, "carbs_g": target_carbs, "fat_g": 14},
                    "ingredients": [
                        f"{int(target_protein * 4.5)}g grilled chicken breast or lean beef",
                        f"{int(target_carbs * 3.5)}g cubed baked sweet potato or jasmine rice",
                        "1 cup baby spinach & steamed broccoli florets",
                        "1 tbsp extra virgin olive oil + honey dijon glaze",
                        "Sea salt & cracked black pepper to taste"
                    ],
                    "instructions": "Toss warm sweet potatoes and sliced grilled chicken over a bed of spinach. Drizzle with honey-dijon glaze. Provides sustained glycogen replenishment and complete amino acids."
                }
            },
            "paleo": {
                "quick_shake": {
                    "title": "Paleo Coconut & Beef Isolate Power Shake",
                    "prep_time_minutes": 4,
                    "target_macros": {"protein_g": target_protein, "carbs_g": target_carbs, "fat_g": 8},
                    "ingredients": [
                        f"{int(target_protein // 25)} scoop(s) Beef Protein Isolate or Egg White Protein",
                        "1 ripe banana + 1 cup tart cherry juice",
                        "250ml pure coconut water",
                        "1 tbsp almond butter",
                        "1 pinch Himalayan pink salt"
                    ],
                    "instructions": "Combine in a high-speed blender for 40 seconds. Tart cherry juice drastically speeds up muscle recovery."
                },
                "whole_food_meal": {
                    "title": "Grass-Fed Beef, Plantain & Avocado Recovery Skillet",
                    "prep_time_minutes": 18,
                    "target_macros": {"protein_g": target_protein, "carbs_g": target_carbs, "fat_g": 16},
                    "ingredients": [
                        f"{int(target_protein * 4.5)}g lean ground bison or grass-fed 90/10 beef",
                        f"{int(target_carbs * 3.0)}g sliced yellow plantains or roasted butternut squash",
                        "1/2 ripe avocado",
                        "1 cup sauteed kale with garlic and olive oil"
                    ],
                    "instructions": "Pan-sear the plantains in coconut oil until golden, brown the seasoned ground beef, and serve alongside kale and avocado."
                }
            },
            "vegan": {
                "quick_shake": {
                    "title": "Ultra-Clean Plant Peptides & Oat Recovery Shake",
                    "prep_time_minutes": 3,
                    "target_macros": {"protein_g": target_protein, "carbs_g": target_carbs, "fat_g": 7},
                    "ingredients": [
                        f"{int(target_protein // 22)} scoop(s) Fermented Pea & Brown Rice Protein Blend",
                        "1/2 cup rolled oats (soaked in almond milk)",
                        "1 large banana + 1 cup frozen mango chunks",
                        "300ml coconut water + 1 tbsp chia seeds",
                        "Pinch of sea salt"
                    ],
                    "instructions": "Blend on high until silky smooth. Delivers complete branched-chain amino acids (BCAAs) with easily digestible carbs."
                },
                "whole_food_meal": {
                    "title": "Crispy Baked Tofu & Edamame Teriyaki Quinoa Bowl",
                    "prep_time_minutes": 22,
                    "target_macros": {"protein_g": target_protein, "carbs_g": target_carbs, "fat_g": 12},
                    "ingredients": [
                        f"{int(target_protein * 3.0)}g high-protein extra firm tofu + 1/2 cup shelled edamame",
                        f"{int(target_carbs * 2.5)}g cooked quinoa or sushi rice",
                        "1 cup steamed snap peas, red bell peppers, and bok choy",
                        "2 tbsp low-sodium tamari teriyaki reduction & sesame seeds"
                    ],
                    "instructions": "Cube and air-fry or bake tofu until crisp. Layer over warm fluffy quinoa with steamed greens and drizzle teriyaki sauce."
                }
            }
        }
        
        # Select matching dietary style or fallback to omnivore
        selected_style = "paleo" if "paleo" in diet_lower else ("vegan" if "vegan" in diet_lower or "vegetarian" in diet_lower else "omnivore")
        recipes = recipe_catalog.get(selected_style, recipe_catalog["omnivore"])
        
        return {
            "dietary_style": selected_style.capitalize(),
            "target_recovery_macros": {
                "protein_grams": target_protein,
                "carbs_grams": target_carbs
            },
            "hydration_and_electrolytes": {
                "water_ml": 750,
                "sodium_mg": 300,
                "potassium_rich_foods": ["Banana", "Coconut water", "Sweet potato"]
            },
            "quick_refuel_option": recipes["quick_shake"],
            "whole_food_option": recipes["whole_food_meal"]
        }
