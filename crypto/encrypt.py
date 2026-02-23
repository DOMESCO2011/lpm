import os
from cryptography.fernet import Fernet
from pathlib import Path

KEY_FILE = Path.home() / "lpm" / "secret.key"

def get_cipher():
    """Returns a Fernet cipher instance, creating the key if it doesn't exist."""
    if not KEY_FILE.exists():
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        os.chmod(KEY_FILE, 0o600)  # Restricted permissions
    else:
        key = KEY_FILE.read_bytes()
    
    return Fernet(key)

def encrypt(plain_text: str) -> str:
    """Encrypts a string and returns a string."""
    cipher = get_cipher()
    return cipher.encrypt(plain_text.encode()).decode()

def decrypt(encrypted_text: str) -> str:
    """Decrypts a string and returns the original text."""
    cipher = get_cipher()
    return cipher.decrypt(encrypted_text.encode()).decode()