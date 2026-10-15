from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.middleware.rate_limiter import limiter
from app.audit.detector import check_brute_force, check_off_hours_access
from app.audit.logger import get_client_ip, log_event, log_login_failed, log_login_success
from jose import JWTError
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.crypto.encryption import blind_index
from app.database import get_db
from app.models import Role, User
from app.schemas import LoginRequest, TokenRefreshRequest, TokenResponse, UserCreate, UserInfo, UserResponse
from app.security import hash_password, verify_password
router = APIRouter(prefix="/auth", tags=["Authentication"])

def primary_role(user: User) -> str:
    return user.roles[0].name if user.roles else "student"

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(409, "Username вже зайнятий")
    if db.query(User).filter(User.email_index == blind_index(user_data.email)).first():
        raise HTTPException(409, "Email вже зареєстровано")
    role = db.query(Role).filter(Role.name == "student").first()
    if role is None:
        raise HTTPException(503, "Систему ще не ініціалізовано")
    user = User(username=user_data.username, email=user_data.email, full_name=user_data.full_name,
                password_hash=hash_password(user_data.password))
    user.roles.append(role)
    db.add(user); db.commit(); db.refresh(user)
    log_event(db,"user_registered","success",get_client_ip(request),user_id=user.id,username=user.username,http_method="POST",endpoint="/auth/register",status_code=201)
    return user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    ip = get_client_ip(request)
    if check_brute_force(db, ip, credentials.username):
        log_login_failed(db, credentials.username, ip, reason="brute_force_blocked")
        raise HTTPException(429, "Забагато невдалих спроб. Спробуйте через 5 хвилин.")
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        log_login_failed(db, credentials.username, ip)
        raise HTTPException(401, "Невірний логін або пароль")
    if not user.is_active:
        log_login_failed(db, credentials.username, ip, reason="inactive")
        raise HTTPException(403, "Акаунт деактивовано")
    check_off_hours_access(db, user.id, user.username, ip)
    log_login_success(db, user.id, user.username, ip)
    return TokenResponse(access_token=create_access_token(user.id, primary_role(user)), refresh_token=create_refresh_token(user.id))

@router.post("/refresh", response_model=TokenResponse)
def refresh(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(401, "Невалідний refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Потрібен refresh token")
    try:
        uid = int(payload["sub"])
    except (ValueError, TypeError, KeyError):
        raise HTTPException(401, "Невалідний refresh token")
    user = db.get(User, uid)
    if user is None or not user.is_active:
        raise HTTPException(401, "Користувача не знайдено")
    return TokenResponse(access_token=create_access_token(user.id, primary_role(user)), refresh_token=create_refresh_token(user.id))

@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user)):
    return UserInfo(id=current_user.id, username=current_user.username, email=current_user.email,
                    full_name=current_user.full_name, roles=[r.name for r in current_user.roles])
