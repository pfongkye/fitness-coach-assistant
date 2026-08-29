import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import dateutil.parser

class WorkoutHistoryLedger:
    """
    Manages encrypted workout session history and executes natural language
    date-based queries, movement filtering, and longitudinal trend analytics.
    """
    def __init__(self):
        # In-memory storage backing or connected to Firestore
        self._records: Dict[str, List[Dict[str, Any]]] = {}

    def log_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Logs a completed session with ISO timestamp and calculated volume metrics."""
        if user_id not in self._records:
            self._records[user_id] = []
            
        record = dict(session_data)
        if "date" not in record:
            record["date"] = datetime.now().strftime("%Y-%m-%d")
        if "timestamp" not in record:
            record["timestamp"] = datetime.now().isoformat()
            
        # Calculate session tonnage if barbell/weight work is present
        tonnage = 0.0
        for exercise in record.get("exercises", []):
            weight = float(exercise.get("weight_kg", 0.0))
            reps = int(exercise.get("reps", 0))
            sets = int(exercise.get("sets", 1))
            tonnage += weight * reps * sets
            
        record["calculated_tonnage_kg"] = round(tonnage, 1)
        self._records[user_id].append(record)
        return record

    def get_session_by_date(self, user_id: str, query_date_str: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves workout session for a given natural date string
        (e.g., 'today', 'yesterday', '2026-08-15', 'last tuesday').
        """
        user_logs = self._records.get(user_id, [])
        if not user_logs:
            return None

        target_date = self._parse_relative_or_iso_date(query_date_str)
        if not target_date:
            return None

        target_date_str = target_date.strftime("%Y-%m-%d")
        for log in reversed(user_logs):
            if log.get("date") == target_date_str:
                return log
        return None

    def query_history(
        self,
        user_id: str,
        movement_filter: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Returns sessions from the past N days, optionally filtered by movement name."""
        user_logs = self._records.get(user_id, [])
        cutoff = datetime.now() - timedelta(days=days_back)
        
        filtered = []
        for log in user_logs:
            log_dt = datetime.fromisoformat(log.get("timestamp", datetime.now().isoformat()))
            if log_dt >= cutoff:
                if movement_filter:
                    # Check if movement matches
                    movements = [m.lower() for m in log.get("movements_performed", [])]
                    if any(movement_filter.lower() in m for m in movements):
                        filtered.append(log)
                else:
                    filtered.append(log)
        return filtered

    def calculate_longitudinal_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Computes volume trends, RPE efficiency, and movement pattern balance over a time window.
        """
        logs = self.query_history(user_id, days_back=days)
        if not logs:
            return {
                "total_sessions": 0,
                "insights": ["No workout sessions found in this time period. Start logging to build insights!"]
            }

        total_tonnage = sum(l.get("calculated_tonnage_kg", 0.0) for l in logs)
        avg_rpe = round(sum(l.get("rpe", 7.0) for l in logs) / len(logs), 1)
        
        # Movement balance tally
        movement_counts: Dict[str, int] = {}
        for l in logs:
            for m in l.get("movements_performed", []):
                movement_counts[m] = movement_counts.get(m, 0) + 1

        insights = []
        if len(logs) >= 3:
            insights.append(f"Completed {len(logs)} sessions over the last {days} days with an average RPE of {avg_rpe}/10.")
            insights.append(f"Total accumulated barbell tonnage: {round(total_tonnage, 1)} kg.")
        
        # Check for neglected movement patterns
        all_movements = " ".join(movement_counts.keys()).lower()
        if "pull" not in all_movements and "row" not in all_movements:
            insights.append("💡 Movement Balance Alert: Vertical/horizontal pulling volume is low. Consider incorporating pull-ups or ring rows in your next session.")
        if "squat" in all_movements and movement_counts.get("Squat", 0) >= 4:
            insights.append("⚡ High leg frequency: You have logged heavy squats frequently. Ensure adequate posterior chain and upper body balance.")

        return {
            "total_sessions": len(logs),
            "total_tonnage_kg": round(total_tonnage, 1),
            "average_rpe": avg_rpe,
            "movement_distribution": movement_counts,
            "coaching_insights": insights
        }

    def _parse_relative_or_iso_date(self, date_str: str) -> Optional[datetime]:
        """Parses colloquial date terms ('today', 'yesterday', 'last tuesday') or ISO strings."""
        s = date_str.strip().lower()
        now = datetime.now()
        
        if s == "today":
            return now
        if s == "yesterday":
            return now - timedelta(days=1)
        
        # Relative weekdays: e.g. "last tuesday", "monday"
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for idx, day in enumerate(weekdays):
            if day in s:
                days_diff = (now.weekday() - idx) % 7
                if days_diff == 0:
                    days_diff = 7  # Last week
                return now - timedelta(days=days_diff)

        # Fallback to dateutil parser
        try:
            return dateutil.parser.parse(date_str)
        except Exception:
            return None

# Global history instance
workout_history_ledger = WorkoutHistoryLedger()
