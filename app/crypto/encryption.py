import hashlib
import hmac
from cryptography.fernet import InvalidToken
from app.crypto.key_manager import get_fernet,get_blind_index_key

DECRYPTION_ERROR='[ПОМИЛКА РОЗШИФРУВАННЯ]'

def encrypt_field(value):
    return get_fernet().encrypt(value.encode('utf-8')).decode('ascii') if value else value

def decrypt_field(value):
    if not value:return value
    try:return get_fernet().decrypt(value.encode('ascii')).decode('utf-8')
    except (InvalidToken, ValueError):return DECRYPTION_ERROR

def blind_index(value):
    return hmac.new(get_blind_index_key(),value.strip().lower().encode(),hashlib.sha256).hexdigest()
