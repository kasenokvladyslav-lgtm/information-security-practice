"""Демонстраційне наповнення БД (не використовуйте тестові паролі у production)."""
from app.database import SessionLocal
from app.models import Grade, Group, Permission, Role, Subject, User
from app.security import hash_password

PERMISSIONS = {
    "read_grades": "Перегляд оцінок", "edit_grades": "Редагування оцінок",
    "read_schedule": "Перегляд розкладу", "manage_users": "Управління користувачами",
    "manage_groups": "Управління групами", "manage_subjects": "Управління дисциплінами",
    "view_reports": "Перегляд звітів",
}
ROLE_MATRIX = {
    "admin": list(PERMISSIONS),
    "teacher": ["read_grades", "edit_grades", "read_schedule", "view_reports"],
    "student": ["read_grades", "read_schedule"],
}

def seed():
    db = SessionLocal()
    try:
        if db.query(Role).first():
            print("Database already seeded.")
            return
        perms = {n: Permission(name=n, description=d) for n, d in PERMISSIONS.items()}
        db.add_all(perms.values())
        roles = {}
        for name, allowed in ROLE_MATRIX.items():
            role = Role(name=name)
            role.permissions = [perms[p] for p in allowed]
            roles[name] = role
        db.add_all(roles.values())
        group = Group(name="КН-31", department="Комп'ютерні науки", year=3)
        subject = Subject(name="Безпека інформаційних систем", credits=4., semester=5)
        db.add_all([group, subject]); db.flush()
        users = [
            User(username="admin", email="admin@university.edu", full_name="Адміністратор Системи", password_hash=hash_password("Admin123!@#")),
            User(username="teacher01", email="teacher@university.edu", full_name="Іваненко Петро Миколайович", password_hash=hash_password("Teacher123!")),
            User(username="student01", email="student@university.edu", full_name="Петренко Марія Олексіївна", password_hash=hash_password("Student123!"), group_id=group.id),
        ]
        for u, name in zip(users, ["admin", "teacher", "student"]):
            u.roles.append(roles[name])
        db.add_all(users); db.flush()
        db.add(Grade(student_id=users[2].id, subject_id=subject.id, grade=92, assigned_by=users[1].id))
        db.commit()
        print("Seed completed successfully!")
        print(f"Roles: {db.query(Role).count()}, Permissions: {db.query(Permission).count()}, Users: {db.query(User).count()}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
