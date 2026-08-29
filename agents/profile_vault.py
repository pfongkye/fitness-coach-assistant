import os
from typing import Dict, Any, List, Optional
from google.adk import Agent
from config.settings import settings
from tools.crypto_tools import KmsEnvelopeCrypto, sanitize_pii_for_llm

crypto = KmsEnvelopeCrypto()
# In-memory mock encrypted store (ready for Firestore/Cloud SQL integration)
_encrypted_user_vault: Dict[str, Dict[str, str]] = {}

def save_athlete_profile(
    user_id: str,
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    city: str,
    training_frequency_per_week: Optional[int] = 3,
    crossfit_experience: Optional[str] = "beginner",
    fitness_level: str = "intermediate",
    dietary_preference: str = "omnivore",
    injury_history: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Encrypts and securely stores the athlete's biometrics, training background, and personal health data
    using Cloud KMS envelope encryption.
    """
    raw_profile = {
        "user_id": user_id,
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "city": city,
        "training_frequency_per_week": training_frequency_per_week,
        "crossfit_experience": crossfit_experience,
        "fitness_level": fitness_level,
        "dietary_preference": dietary_preference,
        "injury_history": injury_history or []
    }
    
    # 1. Encrypt with KMS Envelope
    envelope = crypto.encrypt_payload(raw_profile)
    _encrypted_user_vault[user_id] = envelope
    
    # 2. Return sanitized safe confirmation for the LLM
    safe_view = sanitize_pii_for_llm(raw_profile)
    return {
        "status": "SECURELY_SAVED_ENCRYPTED",
        "encryption": "AES-256-GCM + Cloud KMS Envelope",
        "sanitized_profile": safe_view
    }

def get_athlete_profile(user_id: str) -> Dict[str, Any]:
    """
    Retrieves and decrypts the athlete's profile, returning the sanitized safe view for coaching.
    """
    envelope = _encrypted_user_vault.get(user_id)
    if not envelope:
        return {
            "status": "NOT_REGISTERED",
            "message": "No profile saved yet. Please provide your gender, age, height, weight, training frequency, and CrossFit experience."
        }
    
    decrypted_profile = crypto.decrypt_payload(envelope)
    return {
        "status": "DECRYPTED_SUCCESS",
        "profile": sanitize_pii_for_llm(decrypted_profile)
    }

def check_profile_completeness(user_id: str) -> Dict[str, Any]:
    """
    Validates whether all necessary biometric, training frequency, and experience metrics
    are available for safe, personalized training. NEVER GUESS missing information.
    """
    envelope = _encrypted_user_vault.get(user_id)
    if not envelope:
        return {
            "is_complete": False,
            "missing_fields": ["gender", "age", "height_cm", "weight_kg", "training_frequency_per_week", "crossfit_experience"],
            "prompt_message": (
                "Welcome! To build your personalized, safe training and nutrition plan without guessing, "
                "could you please share:\n"
                "1. Gender\n"
                "2. Age\n"
                "3. Height (cm) and Weight (kg)\n"
                "4. How many times per week do you usually train?\n"
                "5. How long have you known about or practiced CrossFit (e.g. total beginner, 6 months, 3 years)?\n"
                "6. City/location (for localized weather adjustments) and any injuries?"
            )
        }
    
    decrypted_profile = crypto.decrypt_payload(envelope)
    required_keys = ["gender", "age", "height_cm", "weight_kg", "training_frequency_per_week", "crossfit_experience"]
    missing = [k for k in required_keys if decrypted_profile.get(k) is None or decrypted_profile.get(k) == ""]
    
    if missing:
        field_labels = {
            "gender": "Gender",
            "age": "Age",
            "height_cm": "Height (cm)",
            "weight_kg": "Weight (kg)",
            "training_frequency_per_week": "Weekly training frequency",
            "crossfit_experience": "CrossFit experience level / duration"
        }
        missing_prompts = [field_labels.get(m, m) for m in missing]
        return {
            "is_complete": False,
            "missing_fields": missing,
            "prompt_message": f"To deliver accurate, personalized programming without guessing, please provide: {', '.join(missing_prompts)}."
        }
        
    return {
        "is_complete": True,
        "profile": sanitize_pii_for_llm(decrypted_profile),
        "message": "Profile complete."
    }

profile_vault_agent = Agent(
    name="profile_vault_agent",
    model=settings.fast_model,
    description="Securely manages athlete biometrics, training background, injury history, geolocation, and dietary preferences with envelope encryption.",
    instruction=(
        "You are the Biometrics and Profile Security Vault Agent. "
        "Your duty is to store and retrieve athlete health metrics: gender, age, height, weight, city, "
        "training frequency per week, CrossFit experience/knowledge, dietary restrictions, and injury history safely using envelope encryption. "
        "NEVER guess missing biometric or training values. Always use check_profile_completeness to ask for missing information."
    ),
    tools=[save_athlete_profile, get_athlete_profile, check_profile_completeness]
)
