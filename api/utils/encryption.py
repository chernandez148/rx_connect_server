from cryptography.fernet import Fernet
from config import db, app
import base64
import os

def get_encryption_key():
    key = app.config.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("No encryption key configured")
    return base64.urlsafe_b64decode(key)

def encrypt_field(value):
    if value is None:
        return None
    fernet = Fernet(get_encryption_key())
    return fernet.encrypt(value.encode())

def decrypt_field(encrypted):
    if encrypted is None:
        return None
    fernet = Fernet(get_encryption_key())
    return fernet.decrypt(encrypted).decode()