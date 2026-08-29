import json
import os
from typing import Dict, Any, List, Optional

class CrossFitKnowledgeService:
    """
    Exposes verified CrossFit foundational movements, standards, scaling progressions,
    and verified YouTube movement demo videos.
    """
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        movements_path = os.path.join(base_dir, "data", "movements_seed.json")
        benchmarks_path = os.path.join(base_dir, "data", "benchmark_wods.json")
        
        self.movements = []
        self.benchmarks = []
        
        if os.path.exists(movements_path):
            with open(movements_path, "r", encoding="utf-8") as f:
                self.movements = json.load(f).get("movements", [])
                
        if os.path.exists(benchmarks_path):
            with open(benchmarks_path, "r", encoding="utf-8") as f:
                self.benchmarks = json.load(f).get("benchmarks", [])

    def search_movement(self, query: str) -> Optional[Dict[str, Any]]:
        """Finds movement by name or keyword with points of performance & video demo URL."""
        q = query.strip().lower()
        for m in self.movements:
            if q in m["name"].lower() or q in m["id"].lower() or any(q in c.lower() for c in m.get("common_faults", [])):
                return m
        return None

    def get_scaling_guide(self, movement_name: str) -> Dict[str, Any]:
        """Returns scaling ladder and modifications for a movement."""
        m = self.search_movement(movement_name)
        if m:
            return {
                "movement": m["name"],
                "scaling_options": m.get("scaling_options", []),
                "points_of_performance": m.get("points_of_performance", []),
                "video_url": m.get("official_video_url", "")
            }
        return {
            "movement": movement_name,
            "scaling_options": [{"level": "General Scaled", "variation": "Reduce load by 30-50% or replace with dumbbell equivalent."}],
            "video_url": "https://www.youtube.com/@CrossFit"
        }

    def get_benchmark_wod(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves official CrossFit benchmark WOD details (e.g. Fran, Cindy, Murph)."""
        q = name.strip().lower()
        for b in self.benchmarks:
            if q in b["name"].lower():
                return b
        return None

    def list_all_movements(self) -> List[str]:
        """Returns list of all available movement titles."""
        return [m["name"] for m in self.movements]
