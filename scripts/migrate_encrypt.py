from sqlalchemy import text
from app.database import SessionLocal
from app.crypto.encryption import encrypt_field,blind_index

def main():
    db=SessionLocal()
    try:
        rows=db.execute(text('SELECT id,email FROM users WHERE encrypted_email IS NULL AND email IS NOT NULL')).fetchall()
        for user_id,email in rows:
            db.execute(text('UPDATE users SET encrypted_email=:e, email_index=:i WHERE id=:u'),{'e':encrypt_field(email),'i':blind_index(email),'u':user_id})
        db.commit()
        print(f'ENCRYPTED USERS: {len(rows)}')
    except:
        db.rollback();raise
    finally:db.close()
if __name__=='__main__':main()
