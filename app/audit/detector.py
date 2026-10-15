from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import func, or_
from app.models import AuditLog
from app.audit.logger import log_event

def check_brute_force(db,ip,username=None,threshold=5,window_minutes=5):
    since=datetime.utcnow()-timedelta(minutes=window_minutes)
    who=AuditLog.ip_address==ip
    if username:
        who=or_(who,AuditLog.username==username)
    count=db.query(func.count(AuditLog.id)).filter(AuditLog.action=='login_failed',AuditLog.timestamp>=since,who).scalar() or 0
    if count>=threshold:
        log_event(db,'brute_force_detected','warning',ip,username=username,endpoint='/auth/login',details={'failed_attempts':count,'window_minutes':window_minutes})
        return True
    return False

def check_off_hours_access(db,user_id,username,ip):
    hour=datetime.now(ZoneInfo('Europe/Kyiv')).hour
    if 0<=hour<6:
        log_event(db,'off_hours_login','warning',ip,user_id=user_id,username=username,details={'local_hour':hour})
        return True
    return False

def get_security_stats(db,hours=24):
    since=datetime.utcnow()-timedelta(hours=hours)
    counts=dict(db.query(AuditLog.action,func.count(AuditLog.id)).filter(AuditLog.timestamp>=since).group_by(AuditLog.action).all())
    top=db.query(AuditLog.ip_address,func.count(AuditLog.id)).filter(AuditLog.timestamp>=since,AuditLog.status=='failure').group_by(AuditLog.ip_address).order_by(func.count(AuditLog.id).desc()).limit(5).all()
    return {'period_hours':hours,'total_events':sum(counts.values()),'failed_logins':counts.get('login_failed',0),'access_denied':counts.get('access_denied',0),'brute_force_alerts':counts.get('brute_force_detected',0),'off_hours_logins':counts.get('off_hours_login',0),'data_changes':counts.get('data_change',0),'server_errors':counts.get('server_error',0),'top_failure_ips':[{'ip':ip,'failures':n} for ip,n in top]}
