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
    fitness_level: str = "intermediate",
    dietary_preference: str = "omnivore",
    injury_history: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Encrypts and securely stores the athlete's biometrics and personal health data
    using Cloud KMS envelope encryption.
    """
    raw_profile = {
        "user_id": user_id,
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "city": city,
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
        # Default mock profile if not registered yet
        return {
            "status": "NOT_REGISTERED",
            "message": "No profile saved yet. Please provide your age, gender, height, weight, city, and dietary preference."
        }
    
    decrypted_profile = crypto.decrypt_payload(envelope)
    return {
        "status": "DECRYPTED_SUCCESS",
        "profile": sanitize_pii_for_llm(decrypted_profile)
    }

profile_vault_agent = Agent(
    name="profile_vault_agent",
    model=settings.fast_model,
    description="Securely manages athlete biometrics, injury history, geolocation, and dietary preferences with envelope encryption.",
    instruction=(
        "You are the Biometrics and Profile Security Vault Agent. "
        "Your duty is to store and retrieve athlete health metrics, age, gender, height, weight, city, "
        "dietary restrictions, and injury history safely using envelope encryption. "
        "Always confirm that personal data is securely encrypted at rest."
    ),
    tools=[save_athlete_profile, get_athlete_profile]
)
