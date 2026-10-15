import os
from functools import lru_cache
from cryptography.fernet import Fernet, MultiFernet

class EncryptionKeyError(RuntimeError):
    pass

def _load_key(name):
    raw=os.getenv(name)
    if not raw:return None
    try:return Fernet(raw.encode())
    except (ValueError,TypeError) as exc:raise EncryptionKeyError(f'Invalid key: {name}') from exc

@lru_cache(maxsize=1)
def get_fernet():
    current=_load_key('ENCRYPTION_KEY')
    if current is None:raise EncryptionKeyError('ENCRYPTION_KEY missing')
    previous=_load_key('ENCRYPTION_KEY_OLD')
    return MultiFernet([current]+([previous] if previous else []))

@lru_cache(maxsize=1)
def get_blind_index_key():
    raw=os.getenv('BLIND_INDEX_KEY','')
    if len(raw)<32:raise EncryptionKeyError('BLIND_INDEX_KEY missing')
    return raw.encode()
