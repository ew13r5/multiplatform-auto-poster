import os

from cryptography.fernet import Fernet, MultiFernet, InvalidToken


def _get_multi_fernet() -> MultiFernet:
    """Parse FERNET_KEYS from env and create MultiFernet instance.
    First key is active (encryption), all keys used for decryption."""
    keys_str = os.environ.get("FERNET_KEYS", "")
    if not keys_str:
        raise ValueError("FERNET_KEYS not configured")
    keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    if not keys:
        raise ValueError("FERNET_KEYS is empty")
    fernet_instances = [Fernet(k) for k in keys]
    return MultiFernet(fernet_instances)


def encrypt_token(plaintext: str) -> str:
    """Encrypt a plaintext string. Returns base64 ciphertext for DB storage."""
    mf = _get_multi_fernet()
    return mf.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a ciphertext string. Raises InvalidToken on failure."""
    mf = _get_multi_fernet()
    return mf.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
