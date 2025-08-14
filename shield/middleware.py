
# FastAPI version of security middleware (example skeleton)
import logging
import time
import hashlib
from datetime import datetime, timedelta
import jwt
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        # Example: Blocked IPs logic would go here
        # Example: Log request
        response = await call_next(request)
        response_time = time.time() - start_time
        # Example: Log response
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    def get_client_ip(self):
        """Get client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_ip_blocked(self, ip):
        """Check if IP is blocked"""
        if ip in self.blocked_ips:
            block_time = self.blocked_ips[ip]
            # Block for 1 hour
            if datetime.now() - block_time < timedelta(hours=1):
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip):
        """Block an IP address"""
        self.blocked_ips[ip] = datetime.now()
        logger.warning(f"IP {ip} has been blocked")
    
    def record_failed_attempt(self, ip):
        """Record failed authentication attempt"""
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        self.failed_attempts[ip].append(datetime.now())
        
        # Remove attempts older than 1 hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip] 
            if attempt > cutoff_time
        ]
        
        # Block if too many failed attempts
        if len(self.failed_attempts[ip]) >= 5:
            self.block_ip(ip)
    
    def log_request(self):
        """Log incoming request"""
        logger.info(f"Request: {request.method} {request.path} from {self.get_client_ip()}")
    
    def log_response(self, response, response_time):
        """Log outgoing response"""
        logger.info(f"Response: {response.status_code} in {response_time:.3f}s")
    
    def add_security_headers(self):
        """Add security headers to request context"""
        pass

def require_api_key(f):
    """Decorator to require API key authentication"""
    from fastapi import Request, HTTPException
    from functools import wraps
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            api_key = request.headers.get('X-API-Key') if request else None
            expected_key = os.getenv('API_KEY')
            if not expected_key:
                logger.warning("API_KEY not configured")
                raise HTTPException(status_code=500, detail="API authentication not configured")
            if not api_key:
                raise HTTPException(status_code=401, detail="API key required")
            if api_key != expected_key:
                client_ip = request.client.host if request and hasattr(request, 'client') and request.client else "unknown"
                logger.warning(f"Invalid API key attempt from {client_ip}")
                raise HTTPException(status_code=401, detail="Invalid API key")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def generate_api_key():
    """Generate a secure API key"""
    import secrets
    return secrets.token_urlsafe(32)

def hash_sensitive_data(data):
    """Hash sensitive data for logging"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

# Global middleware instance
