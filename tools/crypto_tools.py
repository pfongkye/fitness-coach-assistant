import os
import json
import base64
import hashlib
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class KmsEnvelopeCrypto:
    """
    Implements Envelope Encryption aligned with Google Cloud KMS.
    - Master Key (KEK) is managed via KMS (or local mock for standalone execution).
    - Data Encryption Key (DEK) is generated locally per session/record, encrypts plaintext via AES-256-GCM,
      and DEK is wrapped/encrypted with the KEK.
    """
    def __init__(self, master_key_secret: str = None):
        if not master_key_secret:
            master_key_secret = os.getenv("KMS_MASTER_KEY", "fitness-coach-secret-master-kek-32b!")
        # Ensure 256-bit KEK
        self.kek = hashlib.sha256(master_key_secret.encode()).digest()

    def encrypt_payload(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Encrypts data dictionary using envelope encryption with AES-256-GCM."""
        plaintext = json.dumps(data).encode("utf-8")
        
        # 1. Generate local 256-bit DEK
        dek = AESGCM.generate_key(bit_length=256)
        nonce = os.urandom(12)
        
        # 2. Encrypt plaintext with DEK
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # 3. Wrap (encrypt) DEK with KEK
        kek_aesgcm = AESGCM(self.kek)
        kek_nonce = os.urandom(12)
        wrapped_dek = kek_aesgcm.encrypt(kek_nonce, dek, None)
        
        return {
            "ciphertext_b64": base64.b64encode(ciphertext).decode("utf-8"),
            "nonce_b64": base64.b64encode(nonce).decode("utf-8"),
            "wrapped_dek_b64": base64.b64encode(wrapped_dek).decode("utf-8"),
            "kek_nonce_b64": base64.b64encode(kek_nonce).decode("utf-8")
        }

    def decrypt_payload(self, encrypted_envelope: Dict[str, str]) -> Dict[str, Any]:
        """Unwraps DEK using KEK and decrypts payload."""
        wrapped_dek = base64.b64decode(encrypted_envelope["wrapped_dek_b64"])
        kek_nonce = base64.b64decode(encrypted_envelope["kek_nonce_b64"])
        ciphertext = base64.b64decode(encrypted_envelope["ciphertext_b64"])
        nonce = base64.b64decode(encrypted_envelope["nonce_b64"])
        
        # 1. Unwrap DEK
        kek_aesgcm = AESGCM(self.kek)
        dek = kek_aesgcm.decrypt(kek_nonce, wrapped_dek, None)
        
        # 2. Decrypt ciphertext
        aesgcm = AESGCM(dek)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode("utf-8"))


def sanitize_pii_for_llm(raw_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strips direct personal identifiers (Full Name, Email, Phone, Street Address)
    before feeding profile context to LLM prompt completions.
    Leaves only anonymized demographic, fitness, and geographical tokens.
    """
    safe_profile = {
        "athlete_id": hashlib.sha256(str(raw_profile.get("user_id", "default_user")).encode()).hexdigest()[:8],
        "age": raw_profile.get("age"),
        "gender": raw_profile.get("gender", "unspecified"),
        "height_cm": raw_profile.get("height_cm"),
        "weight_kg": raw_profile.get("weight_kg"),
        "training_frequency_per_week": raw_profile.get("training_frequency_per_week"),
        "crossfit_experience": raw_profile.get("crossfit_experience"),
        "fitness_level": raw_profile.get("fitness_level", "intermediate"),
        "dietary_preference": raw_profile.get("dietary_preference", "omnivore"),
        "injury_history": raw_profile.get("injury_history", []),
        "city": raw_profile.get("city", "Local"),
        "country": raw_profile.get("country", "")
    }
    return {k: v for k, v in safe_profile.items() if v is not None}
