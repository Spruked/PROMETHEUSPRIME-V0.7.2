
# FastAPI version of security middleware (example skeleton)
import logging
import hashlib
from datetime import datetime, timedelta
import jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, dispatch: object = None) -> None:
        super().__init__(app, dispatch)
        self.blocked_ips: dict[str, datetime] = {}
        self.failed_attempts: dict[str, list[datetime]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
    # start_time = time.time()  # Removed unused variable
        # Example: Blocked IPs logic would go here
        # Example: Log request
        response = await call_next(request)
        # Example: Log response
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    @staticmethod
    def get_client_ip(request: Request) -> str:
        xff = request.headers.get('X-Forwarded-For')
        if xff:
            return xff.split(',')[0].strip()
        xri = request.headers.get('X-Real-IP')
        if xri:
            return xri
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def is_ip_blocked(self, ip: str) -> bool:
        if ip in self.blocked_ips:
            block_time = self.blocked_ips[ip]
            # Block for 1 hour
            if datetime.now() - block_time < timedelta(hours=1):
                return True
            else:
                del self.blocked_ips[ip]
        return False

    def block_ip(self, ip: str) -> None:
        self.blocked_ips[ip] = datetime.now()
        logger.warning(f"IP {ip} has been blocked")

    def record_failed_attempt(self, ip: str) -> None:
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

    @staticmethod
    def log_request(request: Request) -> None:
        logger.info(f"Request: {request.method} {request.url.path} from {SecurityMiddleware.get_client_ip(request)}")

    @staticmethod
    def log_response(response: Response, response_time: float) -> None:
        logger.info(f"Response: {response.status_code} in {response_time:.3f}s")

    def add_security_headers(self):
        pass


def generate_api_key():
    """Generate a secure API key"""
    import secrets
    return secrets.token_urlsafe(32)

def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

# Global middleware instance
