import pytest
from tools.crypto_tools import KmsEnvelopeCrypto, sanitize_pii_for_llm

def test_kms_envelope_encryption_cycle():
    crypto = KmsEnvelopeCrypto()
    sample_data = {
        "user_id": "athlete_123",
        "name": "Alex Dupont",
        "email": "alex@example.com",
        "age": 30,
        "weight_kg": 75.5,
        "injury_history": ["ACL tear 2022"]
    }
    
    # 1. Encrypt
    encrypted_envelope = crypto.encrypt_payload(sample_data)
    assert "ciphertext_b64" in encrypted_envelope
    assert "wrapped_dek_b64" in encrypted_envelope
    assert "nonce_b64" in encrypted_envelope
    assert "kek_nonce_b64" in encrypted_envelope
    
    # 2. Decrypt
    decrypted = crypto.decrypt_payload(encrypted_envelope)
    assert decrypted["user_id"] == "athlete_123"
    assert decrypted["name"] == "Alex Dupont"
    assert decrypted["weight_kg"] == 75.5
    assert decrypted["injury_history"] == ["ACL tear 2022"]

def test_pii_sanitization_for_llm():
    raw_data = {
        "user_id": "athlete_123",
        "name": "Alex Dupont",
        "email": "alex@example.com",
        "phone": "+33612345678",
        "age": 30,
        "gender": "male",
        "height_cm": 178.0,
        "weight_kg": 75.5,
        "city": "Paris",
        "country": "France",
        "injury_history": ["ACL tear 2022"]
    }
    
    safe_view = sanitize_pii_for_llm(raw_data)
    # Ensure PII is stripped
    assert "name" not in safe_view
    assert "email" not in safe_view
    assert "phone" not in safe_view
    
    # Ensure fitness context is preserved
    assert safe_view["age"] == 30
    assert safe_view["weight_kg"] == 75.5
    assert safe_view["city"] == "Paris"
    assert "athlete_id" in safe_view
