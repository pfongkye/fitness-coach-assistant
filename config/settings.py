import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Automatically load environment variables from local .env if present
load_dotenv()

class CoachSettings(BaseModel):
    """Global configuration settings for the AI Fitness Coach Assistant."""
    app_name: str = "Expert AI Fitness Coach"
    version: str = "1.0.0"
    
    # Model Configuration (Gemini Flash tier across all agents)
    default_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    fast_model: str = os.getenv("GEMINI_FAST_MODEL", "gemini-2.5-flash")
    
    # Google Cloud & Security settings
    gcp_project_id: str = os.getenv("GCP_PROJECT", "fitness-coach-dev")
    gcp_region: str = os.getenv("GCP_REGION", "us-central1")
    kms_key_ring: str = os.getenv("KMS_KEY_RING", "fitness-vault-ring")
    kms_crypto_key: str = os.getenv("KMS_KEY", "user-data-key")
    
    # State & Persistence
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    firestore_collection_users: str = "fitness_users"
    firestore_collection_workouts: str = "workout_history"
    firestore_collection_prs: str = "personal_records"
    
    # Weather Integration
    weather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    weather_provider: str = os.getenv("WEATHER_PROVIDER", "open-meteo")  # default open-meteo (no key needed)
    
    # Gamification Parameters
    xp_per_workout: int = 100
    xp_per_post_checkin: int = 25
    xp_per_pr: int = 150
    monthly_streak_freezes: int = 2

settings = CoachSettings()
