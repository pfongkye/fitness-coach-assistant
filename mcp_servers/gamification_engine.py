from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class GamificationEngineService:
    """
    Manages XP, level progression, PR tracking, streak maintenance with 'Freeze Tokens',
    and weekly fitness quests based on the Octalysis gamification framework.
    """
    def __init__(self):
        # In-memory storage backing or connected to Firestore
        self._user_gamification: Dict[str, Dict[str, Any]] = {}

    def _get_or_create_user(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self._user_gamification:
            self._user_gamification[user_id] = {
                "xp": 0,
                "level": 1,
                "current_streak_days": 0,
                "longest_streak_days": 0,
                "last_activity_date": None,
                "freeze_tokens_remaining": 2,
                "badges_unlocked": ["Rookie Onboarded 🏅"],
                "prs": {},
                "active_quests": [
                    {"id": "q1", "title": "Consistency Starter", "goal": "Log 3 workouts this week", "progress": 0, "target": 3, "reward_xp": 150, "completed": False},
                    {"id": "q2", "title": "Check-in Discipline", "goal": "Complete post-workout check-in", "progress": 0, "target": 1, "reward_xp": 50, "completed": False}
                ]
            }
        return self._user_gamification[user_id]

    def award_xp(self, user_id: str, xp_amount: int, activity_label: str) -> Dict[str, Any]:
        """Awards XP, updates level, and updates streaks with freeze token protection."""
        user = self._get_or_create_user(user_id)
        user["xp"] += xp_amount
        
        # Calculate Level (each level requires Level * 250 XP)
        old_level = user["level"]
        new_level = max(1, int((user["xp"] / 250.0) ** 0.6) + 1)
        leveled_up = new_level > old_level
        user["level"] = new_level
        
        # Update streak
        today_str = datetime.now().strftime("%Y-%m-%d")
        last_date_str = user["last_activity_date"]
        
        if last_date_str != today_str:
            if last_date_str:
                last_dt = datetime.strptime(last_date_str, "%Y-%m-%d")
                days_diff = (datetime.now() - last_dt).days
                if days_diff == 1:
                    user["current_streak_days"] += 1
                elif days_diff == 2 and user["freeze_tokens_remaining"] > 0:
                    # Use streak freeze token
                    user["freeze_tokens_remaining"] -= 1
                    user["current_streak_days"] += 1
                    user["badges_unlocked"].append("Streak Saved by Freeze Token ❄️")
                elif days_diff > 1:
                    user["current_streak_days"] = 1
            else:
                user["current_streak_days"] = 1
                
            user["last_activity_date"] = today_str
            if user["current_streak_days"] > user["longest_streak_days"]:
                user["longest_streak_days"] = user["current_streak_days"]

        # Update quest progress
        for q in user["active_quests"]:
            if not q["completed"]:
                q["progress"] = min(q["target"], q["progress"] + 1)
                if q["progress"] >= q["target"]:
                    q["completed"] = True
                    user["xp"] += q["reward_xp"]
                    user["badges_unlocked"].append(f"Quest Master: {q['title']} 🏆")

        return {
            "awarded_xp": xp_amount,
            "total_xp": user["xp"],
            "level": user["level"],
            "leveled_up": leveled_up,
            "current_streak_days": user["current_streak_days"],
            "freeze_tokens": user["freeze_tokens_remaining"],
            "activity": activity_label
        }

    def log_pr(self, user_id: str, movement: str, value: str) -> Dict[str, Any]:
        """Logs a Personal Record (PR) and awards achievement bonus."""
        user = self._get_or_create_user(user_id)
        user["prs"][movement] = {
            "value": value,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        badge_name = f"PR: {movement} ({value}) 🚀"
        if badge_name not in user["badges_unlocked"]:
            user["badges_unlocked"].append(badge_name)
            
        reward = self.award_xp(user_id, 150, f"New Personal Record on {movement}")
        reward["new_badge"] = badge_name
        return reward

    def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """Returns comprehensive gamification stats for the athlete."""
        user = self._get_or_create_user(user_id)
        return {
            "level": user["level"],
            "xp": user["xp"],
            "next_level_xp": int(((user["level"]) ** (1 / 0.6)) * 250),
            "current_streak_days": user["current_streak_days"],
            "longest_streak_days": user["longest_streak_days"],
            "freeze_tokens": user["freeze_tokens_remaining"],
            "badges": user["badges_unlocked"],
            "prs": user["prs"],
            "active_quests": user["active_quests"]
        }

# Global singleton instance
gamification_service = GamificationEngineService()
