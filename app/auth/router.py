from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Role, User
from app.schemas import LoginRequest, LoginResponse, UserCreate, UserResponse
from app.security import hash_password, verify_password
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(409, "Username вже зайнятий")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(409, "Email вже зареєстровано")
    role = db.query(Role).filter(Role.name == "student").first()
    if role is None:
        raise HTTPException(503, "Систему ще не ініціалізовано")
    new_user = User(username=user_data.username, email=user_data.email,
                    full_name=user_data.full_name, password_hash=hash_password(user_data.password))
    new_user.roles.append(role)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(401, "Невірний логін або пароль")
    if not user.is_active:
        raise HTTPException(403, "Акаунт деактивовано")
    return LoginResponse(message="Вхід успішний", user_id=user.id, username=user.username,
                         roles=[r.name for r in user.roles])
