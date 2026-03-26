import os
import pytest
from unittest.mock import patch
from cryptography.fernet import Fernet, InvalidToken


def _gen_key():
    return Fernet.generate_key().decode()


def test_encrypt_decrypt_roundtrip():
    key = _gen_key()
    with patch.dict(os.environ, {"FERNET_KEYS": key}):
        from app.services.encryption import encrypt_token, decrypt_token
        plaintext = "my-secret-token-123"
        encrypted = encrypt_token(plaintext)
        assert encrypted != plaintext
        assert decrypt_token(encrypted) == plaintext


def test_encrypt_returns_different_than_input():
    key = _gen_key()
    with patch.dict(os.environ, {"FERNET_KEYS": key}):
        from app.services.encryption import encrypt_token
        result = encrypt_token("secret")
        assert result != "secret"


def test_decrypt_invalid_raises():
    key = _gen_key()
    with patch.dict(os.environ, {"FERNET_KEYS": key}):
        from app.services.encryption import decrypt_token
        with pytest.raises(Exception):
            decrypt_token("not-valid-ciphertext")


def test_multifernet_rotation():
    key_old = _gen_key()
    key_new = _gen_key()
    # Encrypt with old key
    with patch.dict(os.environ, {"FERNET_KEYS": key_old}):
        from app.services.encryption import encrypt_token
        encrypted = encrypt_token("rotate-me")
    # Decrypt with new key first, old key second
    with patch.dict(os.environ, {"FERNET_KEYS": f"{key_new},{key_old}"}):
        from app.services.encryption import decrypt_token
        assert decrypt_token(encrypted) == "rotate-me"
