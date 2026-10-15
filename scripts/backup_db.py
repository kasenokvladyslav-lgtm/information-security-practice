import hashlib
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from app.crypto.key_manager import get_fernet

DB=Path('data/app.db')
BACKUPS=Path('data/backups')
def backup():
    BACKUPS.mkdir(parents=True,exist_ok=True)
    fd,path=tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        source=sqlite3.connect(DB)
        dest=sqlite3.connect(path)
        try:source.backup(dest)
        finally:source.close();dest.close()
        encrypted=get_fernet().encrypt(Path(path).read_bytes())
    finally:Path(path).unlink(missing_ok=True)
    out=BACKUPS/('app_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')+'.db.enc')
    out.write_bytes(encrypted);out.chmod(0o600)
    for old in sorted(BACKUPS.glob('app_*.db.enc'))[:-7]:old.unlink()
    print(f'ENCRYPTED BACKUP OK: {out}, SHA256={hashlib.sha256(encrypted).hexdigest()}')
    return out
if __name__=='__main__':backup()
