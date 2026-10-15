import sqlite3
import sys
from pathlib import Path
from app.crypto.key_manager import get_fernet

def restore(source,target='data/restore_test.db'):
    content=get_fernet().decrypt(Path(source).read_bytes())
    p=Path(target);p.write_bytes(content)
    with sqlite3.connect(p) as c:
        integrity=c.execute('PRAGMA integrity_check').fetchone()[0]
        users=c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    print('RESTORE integrity_check=',integrity,' users=',users)
    if integrity!='ok':raise RuntimeError('Backup failed integrity check')
if __name__=='__main__':restore(sys.argv[1])
