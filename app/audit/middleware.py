import time
from fastapi import Request
from jose import JWTError
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from app.audit.logger import get_client_ip,log_event
from app.auth.jwt_handler import verify_token
from app.database import SessionLocal

SKIP={'/health','/docs','/redoc','/openapi.json','/favicon.ico'}
ACTIONS={401:'unauthorized',403:'access_denied',429:'rate_limited'}

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request,call_next):
        if request.url.path in SKIP:
            return await call_next(request)
        start=time.perf_counter()
        response=await call_next(request)
        code=response.status_code
        if request.method=='GET' and code<400:
            return response
        auth=request.headers.get('authorization','')
        uid=None
        if auth.lower().startswith('bearer '):
            try: uid=int(verify_token(auth[7:]).get('sub'))
            except (JWTError,ValueError,TypeError): pass
        action='server_error' if code>=500 else ACTIONS.get(code,'http_'+request.method.lower())
        status='error' if code>=500 else ('failure' if code>=400 else 'success')
        ip=get_client_ip(request);method=request.method;endpoint=request.url.path
        duration=round((time.perf_counter()-start)*1000,1)
        def write():
            db=SessionLocal()
            try:log_event(db,action,status,ip,user_id=uid,http_method=method,endpoint=endpoint,status_code=code,details={'duration_ms':duration})
            finally:db.close()
        await run_in_threadpool(write)
        return response
