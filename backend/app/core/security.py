from werkzeug.security import generate_password_hash, check_password_hash
import secrets

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)

def generate_session_token() -> str:
    return secrets.token_urlsafe(48)