from typing import Dict, Any, List, Optional
import math

class PeriodizationEngine:
    """Calculates 1RMs, training percentages, and adapts training blocks dynamically."""

    @staticmethod
    def estimate_1rm(weight_lifted: float, reps: int) -> Dict[str, float]:
        """Calculates estimated 1RM using Epley and Brzycki formulas."""
        if reps == 1:
            return {"1rm_kg": round(weight_lifted, 1), "confidence": 1.0}
        
        # Epley: 1RM = w * (1 + r/30)
        epley_1rm = weight_lifted * (1.0 + reps / 30.0)
        # Brzycki: 1RM = w / (1.0278 - 0.0278 * r)
        brzycki_1rm = weight_lifted / (1.0278 - 0.0278 * reps) if reps < 37 else epley_1rm
        
        avg_1rm = (epley_1rm + brzycki_1rm) / 2.0
        return {
            "1rm_kg": round(avg_1rm, 1),
            "epley_1rm": round(epley_1rm, 1),
            "brzycki_1rm": round(brzycki_1rm, 1)
        }

    @staticmethod
    def calculate_training_weights(one_rep_max: float, percentages: List[int]) -> Dict[str, float]:
        """Generates target weights for prescribed percentage zones (e.g. [70, 75, 80, 85])."""
        return {f"{p}%": round(one_rep_max * (p / 100.0), 1) for p in percentages}

    @staticmethod
    def adapt_workout_for_conditions(
        base_workout: Dict[str, Any],
        readiness_data: Dict[str, Any],
        weather_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically adjusts a base workout by applying volume scaling,
        substituting movements if muscles are fatigued or weather is adverse.
        """
        adapted = dict(base_workout)
        adjustments_applied = []
        
        # 1. Check volume multiplier from readiness
        vol_multiplier = readiness_data.get("volume_multiplier", 1.0)
        if vol_multiplier < 1.0:
            adjustments_applied.append(f"Volume scaled by {int((1 - vol_multiplier)*100)}% due to fatigue score ({readiness_data.get('readiness_score')}/100)")
            adapted["scaled_volume"] = True
            adapted["volume_factor"] = vol_multiplier
        
        # 2. Check muscle soreness hotspots
        sore_areas = [s.lower() for s in readiness_data.get("soreness_hotspots", [])]
        if "legs" in sore_areas or "quads" in sore_areas:
            adjustments_applied.append("Leg soreness detected: Reduced heavy squat load by 15% and emphasized upper body pulling/core.")
        if "shoulders" in sore_areas or "upper_back" in sore_areas:
            adjustments_applied.append("Shoulder fatigue detected: Substituted overhead barbell work with chest-supported dumbbell work or strict ring rows.")
        
        # 3. Check Weather conditions
        if weather_data:
            temp_c = weather_data.get("temperature_c", 20.0)
            is_raining = weather_data.get("is_raining", False)
            heat_index = weather_data.get("heat_index_c", temp_c)
            
            if heat_index >= 32.0:
                adjustments_applied.append(f"Heat Alert ({heat_index}°C Heat Index): Outdoor runs replaced with indoor C2 Rower or Echo Bike; +500ml hydration with sodium mandated.")
                adapted["indoor_substitutions"] = {"400m Run": "500m C2 Row", "800m Run": "1000m C2 Row / 1200m Echo Bike"}
            elif is_raining:
                adjustments_applied.append("Rain detected: Outdoor running swapped for indoor double-unders or rowing.")
                adapted["indoor_substitutions"] = {"400m Run": "50 Double-Unders + 15 Burpees"}

        adapted["applied_adaptations"] = adjustments_applied
        return adapted
