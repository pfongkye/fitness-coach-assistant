import pytest
from datetime import datetime, timedelta
from tools.history_tools import WorkoutHistoryLedger

def test_workout_history_logging_and_date_queries():
    ledger = WorkoutHistoryLedger()
    user_id = "test_athlete"
    today_str = datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 1. Log workout for today
    session_today = {
        "date": today_str,
        "timestamp": datetime.now().isoformat(),
        "completed_score": "12:30 RX",
        "rpe": 8.0,
        "movements_performed": ["Thruster", "Pull-Up"],
        "exercises": [
            {"name": "Thruster", "weight_kg": 43.0, "sets": 3, "reps": 15}
        ]
    }
    ledger.log_session(user_id, session_today)
    
    # 2. Log workout for yesterday
    session_yesterday = {
        "date": yesterday_str,
        "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
        "completed_score": "5x5 @ 120kg",
        "rpe": 7.5,
        "movements_performed": ["Deadlift"],
        "exercises": [
            {"name": "Deadlift", "weight_kg": 120.0, "sets": 5, "reps": 5}
        ]
    }
    ledger.log_session(user_id, session_yesterday)
    
    # 3. Query "today"
    res_today = ledger.get_session_by_date(user_id, "today")
    assert res_today is not None
    assert res_today["date"] == today_str
    assert "Thruster" in res_today["movements_performed"]
    assert res_today["calculated_tonnage_kg"] == 43.0 * 3 * 15  # 1935 kg
    
    # 4. Query "yesterday"
    res_yesterday = ledger.get_session_by_date(user_id, "yesterday")
    assert res_yesterday is not None
    assert res_yesterday["date"] == yesterday_str
    assert "Deadlift" in res_yesterday["movements_performed"]
    assert res_yesterday["calculated_tonnage_kg"] == 120.0 * 5 * 5  # 3000 kg

def test_longitudinal_trends():
    ledger = WorkoutHistoryLedger()
    user_id = "test_athlete_trends"
    
    for i in range(5):
        dt = datetime.now() - timedelta(days=i*2)
        ledger.log_session(user_id, {
            "date": dt.strftime("%Y-%m-%d"),
            "timestamp": dt.isoformat(),
            "completed_score": f"Session {i}",
            "rpe": 8.0,
            "movements_performed": ["Back Squat", "Bench Press"],
            "exercises": [{"name": "Back Squat", "weight_kg": 100.0, "sets": 3, "reps": 5}]
        })
        
    trends = ledger.calculate_longitudinal_trends(user_id, days=30)
    assert trends["total_sessions"] == 5
    assert trends["total_tonnage_kg"] == 5 * (100.0 * 3 * 5)  # 7500 kg
    assert trends["average_rpe"] == 8.0
    assert len(trends["coaching_insights"]) > 0
