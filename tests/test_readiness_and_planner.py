import pytest
from tools.readiness_tools import ReadinessEngine, PreSessionCheckin, PostSessionCheckin
from mcp_servers.crossfit_knowledge import CrossFitKnowledgeService

def test_pre_session_readiness_evaluation():
    # 1. High energy, good sleep
    checkin_fresh = PreSessionCheckin(
        energy_level=5,
        sleep_quality="excellent",
        soreness_areas=[],
        soreness_severity=1
    )
    result_fresh = ReadinessEngine.evaluate_pre_session(checkin_fresh)
    assert result_fresh["readiness_score"] >= 90.0
    assert result_fresh["adaptation_tier"] == "OPTIMAL_PROGRESSION"
    assert result_fresh["volume_multiplier"] == 1.0

    # 2. Low energy, poor sleep, high soreness
    checkin_fatigued = PreSessionCheckin(
        energy_level=1,
        sleep_quality="poor",
        soreness_areas=["quads", "lower_back"],
        soreness_severity=9
    )
    result_fatigued = ReadinessEngine.evaluate_pre_session(checkin_fatigued)
    assert result_fatigued["readiness_score"] <= 35.0
    assert result_fatigued["volume_multiplier"] <= 0.70

def test_post_session_checkin_and_medical_disclaimer():
    checkin_pain = PostSessionCheckin(
        rpe=9.0,
        completed_score="15:00",
        soreness_hotspots=["shoulders"],
        acute_joint_pain=True,
        feedback_notes="Felt sharp pinch in right rotator cuff on last round of thrusters."
    )
    result_pain = ReadinessEngine.evaluate_post_session(checkin_pain)
    assert result_pain["is_high_strain"] is True
    assert result_pain["safety_warning"] is not None
    assert "MEDICAL DISCLAIMER" in result_pain["safety_warning"]

def test_crossfit_movement_knowledge_search():
    kb = CrossFitKnowledgeService()
    snatch = kb.search_movement("Snatch")
    assert snatch is not None
    assert snatch["name"] == "Squat Snatch / Full Snatch"
    assert len(snatch["points_of_performance"]) > 0
    assert "youtube.com" in snatch["official_video_url"]
