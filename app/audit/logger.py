import json
import logging
from sqlalchemy.orm import Session
from app.models import AuditLog

logger = logging.getLogger("security_audit")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(h)
logger.setLevel(logging.INFO)
logger.propagate = False
SENSITIVE = {"password", "token", "access_token", "refresh_token", "secret", "key", "email", "phone"}

def get_client_ip(request):
    return request.client.host if request.client else "unknown"

def log_event(db: Session, action: str, status: str, ip_address: str, *, user_id=None, username=None, http_method=None, endpoint=None, status_code=None, resource=None, details=None):
    clean = {k: ("[redacted]" if k.lower() in SENSITIVE else v) for k,v in (details or {}).items()}
    event = dict(action=action, status=status, user_id=user_id, username=username, ip_address=ip_address, endpoint=endpoint, status_code=status_code, details=clean)
    try:
        db.add(AuditLog(user_id=user_id, username=username, ip_address=ip_address, action=action, resource=resource, http_method=http_method, endpoint=endpoint, status=status, status_code=status_code, details=json.dumps(clean,ensure_ascii=False) if clean else None))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception('audit_write_failed')
    logger.info(json.dumps(event,ensure_ascii=False))

def log_login_success(db,user_id,username,ip):
    log_event(db,'login_success','success',ip,user_id=user_id,username=username,http_method='POST',endpoint='/auth/login',status_code=200)

def log_login_failed(db,username,ip,reason='invalid_credentials'):
    log_event(db,'login_failed','failure',ip,username=username,http_method='POST',endpoint='/auth/login',status_code=401,details={'reason':reason})

def log_data_change(db,user,ip,resource,old,new,endpoint=None):
    log_event(db,'data_change','success',ip,user_id=user.id,username=user.username,resource=resource,endpoint=endpoint,details={'old':old,'new':new})
