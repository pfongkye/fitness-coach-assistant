from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PreSessionCheckin(BaseModel):
    energy_level: int = Field(..., ge=1, le=5, description="Energy rating from 1 (exhausted) to 5 (peak energy)")
    sleep_quality: str = Field(..., description="Subjective sleep rating: 'poor', 'fair', 'good', 'excellent'")
    soreness_areas: List[str] = Field(default_factory=list, description="List of sore muscle groups (e.g. 'legs', 'shoulders', 'lower_back')")
    soreness_severity: int = Field(default=3, ge=1, le=10, description="Overall soreness severity 1-10")
    notes: Optional[str] = Field(default="", description="Any subjective notes (e.g., stressful workday, feeling light)")

class PostSessionCheckin(BaseModel):
    rpe: float = Field(..., ge=1.0, le=10.0, description="Borg CR10 Rate of Perceived Exertion (1 = very light, 10 = max)")
    completed_score: str = Field(..., description="Result, e.g., '14:20 RX', '5 rounds + 12 reps', '5x5 @ 100kg'")
    soreness_hotspots: List[str] = Field(default_factory=list, description="Muscle groups experiencing high fatigue/pump")
    acute_joint_pain: bool = Field(default=False, description="Did you feel sharp joint/tendon pain (triggering medical alert)?")
    feedback_notes: Optional[str] = Field(default="", description="Athlete notes on pacing, barbell feeling, or mindset")

class ReadinessEngine:
    """Computes readiness score and training adaptation triggers from subjective check-ins."""

    @staticmethod
    def evaluate_pre_session(checkin: PreSessionCheckin) -> Dict[str, Any]:
        """Calculates Readiness Index (0-100) and prescribes volume/intensity adjustments."""
        # 1. Base score from energy (1-5 maps to 20-100)
        energy_score = checkin.energy_level * 20.0
        
        # 2. Sleep modifier
        sleep_weights = {
            "poor": -20.0,
            "fair": -5.0,
            "good": +5.0,
            "excellent": +15.0
        }
        sleep_mod = sleep_weights.get(checkin.sleep_quality.lower(), 0.0)
        
        # 3. Soreness penalty
        soreness_penalty = (checkin.soreness_severity / 10.0) * 25.0
        
        readiness_score = max(10.0, min(100.0, energy_score + sleep_mod - soreness_penalty))
        
        # 4. Determine training adaptation strategy
        if readiness_score >= 80.0:
            recommendation = "OPTIMAL_PROGRESSION"
            volume_multiplier = 1.0
            coach_advice = "You're primed for high output! Target prescribed percentages or aim for a solid pacing strategy."
        elif readiness_score >= 55.0:
            recommendation = "MODERATE_MAINTENANCE"
            volume_multiplier = 0.85
            coach_advice = "Solid baseline. Warm up thoroughly, monitor working sets, and adjust load if fatigue creeps in."
        elif readiness_score >= 35.0:
            recommendation = "SCALED_DELOAD"
            volume_multiplier = 0.70
            coach_advice = "High fatigue detected. We'll reduce heavy loading by 25-30% and focus on crisp technique and steady aerobic pacing."
        else:
            recommendation = "ACTIVE_RECOVERY_MOBILITY"
            volume_multiplier = 0.40
            coach_advice = "Recovery priority today. Switch to a 20-min gentle nasal-breathing flush, soft tissue work, and targeted mobility."

        return {
            "readiness_score": round(readiness_score, 1),
            "adaptation_tier": recommendation,
            "volume_multiplier": volume_multiplier,
            "soreness_hotspots": checkin.soreness_areas,
            "coach_advice": coach_advice
        }

    @staticmethod
    def evaluate_post_session(checkin: PostSessionCheckin) -> Dict[str, Any]:
        """Analyzes session completion to update fatigue ledgers and safety warnings."""
        is_high_strain = checkin.rpe >= 8.5
        
        # Medical Safety Alert
        safety_warning = None
        if checkin.acute_joint_pain:
            safety_warning = (
                "⚠️ MEDICAL DISCLAIMER: You reported sharp joint or tendon pain. Please rest the affected joint, "
                "apply ice/compression as appropriate, and consult a licensed physical therapist or physician if pain persists. "
                "We will automatically modify tomorrow's workout to avoid loading this joint."
            )
        
        return {
            "rpe": checkin.rpe,
            "is_high_strain": is_high_strain,
            "soreness_hotspots": checkin.soreness_hotspots,
            "safety_warning": safety_warning,
            "glycogen_depletion_level": "HIGH" if checkin.rpe >= 8.0 else ("MODERATE" if checkin.rpe >= 5.0 else "LOW"),
            "post_session_summary": f"Completed: {checkin.completed_score} | RPE: {checkin.rpe}/10"
        }
