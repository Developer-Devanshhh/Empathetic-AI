import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Generate a default key if none exists (for dev convenience only)
# In prod, this must come from env and be persistent.
_env_key = os.getenv("ENCRYPTION_KEY")
if not _env_key:
    # Generate a throwaway key for dev session if missing, but printing warning
    print("[WARNING] ENCRYPTION_KEY not found in .env. Using ephemeral key (DATA WILL BE LOST ON RESTART).")
    _key = Fernet.generate_key()
else:
    _key = _env_key.encode() if isinstance(_env_key, str) else _env_key

cipher_suite = Fernet(_key)

def encrypt_text(text: str) -> str:
    """Encrypts a string using Fernet (AES-128-CBC + HMAC)."""
    if not text: 
        return ""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_text(text: str) -> str:
    """Decrypts a string using Fernet."""
    if not text: 
        return ""
    try:
        return cipher_suite.decrypt(text.encode()).decode()
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")
        return "[ENCRYPTED_DATA_ERROR]"
