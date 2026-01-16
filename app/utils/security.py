from cryptography.fernet import Fernet
import os

# In a real app, this should be in .env. For MVP, we generate/load from a file.
KEY_FILE = "secret.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

key = load_key()
cipher_suite = Fernet(key)

def encrypt_text(text: str) -> str:
    if not text:
        return ""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text: str) -> str:
    if not encrypted_text:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return "[Decryption Failed]"
