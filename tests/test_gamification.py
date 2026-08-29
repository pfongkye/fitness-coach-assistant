import pytest
from mcp_servers.gamification_engine import GamificationEngineService

def test_gamification_xp_and_leveling():
    game = GamificationEngineService()
    user_id = "test_user_game"
    
    # 1. Initial overview
    overview = game.get_profile_summary(user_id)
    assert overview["level"] == 1
    assert overview["xp"] == 0
    assert overview["freeze_tokens"] == 2
    
    # 2. Award XP (Base 300 XP + 50 XP bonus from completed quest q2)
    res = game.award_xp(user_id, 300, "Workout Logged")
    assert res["total_xp"] >= 300
    assert res["level"] >= 1
    assert res["current_streak_days"] == 1
    
    # 3. Log PR (+150 XP bonus)
    pr_res = game.log_pr(user_id, "Clean & Jerk", "100kg")
    assert "PR: Clean & Jerk (100kg)" in pr_res["new_badge"]
    assert pr_res["total_xp"] >= 450
