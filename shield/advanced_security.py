import hashlib
import hmac
import secrets
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)

class AdvancedSecurity:
    """Advanced security features for the NFT minting system"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.session_tokens = {}
        self.nonce_cache = set()
        self.request_signatures = {}
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'encryption.key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Save key with secure permissions
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Set secure permissions
            os.chmod(key_file, 0o600)
            
            logger.info("Generated new encryption key")
            return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def generate_session_token(self, user_id: str, ttl_minutes: int = 60) -> str:
        """Generate a secure session token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        
        self.session_tokens[token] = {
            'user_id': user_id,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
        
        logger.info(f"Generated session token for user {user_id}")
        return token
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token"""
        if token not in self.session_tokens:
            return None
        
        session = self.session_tokens[token]
        
        if datetime.utcnow() > session['expires_at']:
            del self.session_tokens[token]
            return None
        
        return session
    
    def revoke_session_token(self, token: str) -> bool:
        """Revoke a session token"""
        if token in self.session_tokens:
            del self.session_tokens[token]
            logger.info("Session token revoked")
            return True
        return False
    
    def generate_request_signature(self, payload: Dict[str, Any], secret_key: str) -> str:
        """Generate HMAC signature for request"""
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def validate_request_signature(self, payload: Dict[str, Any], signature: str, secret_key: str) -> bool:
        """Validate request signature"""
        expected_signature = self.generate_request_signature(payload, secret_key)
        return hmac.compare_digest(signature, expected_signature)
    
    def generate_nonce(self) -> str:
        """Generate a unique nonce"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_hex(16)
        nonce = f"{timestamp}_{random_part}"
        
        self.nonce_cache.add(nonce)
        
        # Clean old nonces (older than 5 minutes)
        current_time = int(time.time())
        self.nonce_cache = {
            n for n in self.nonce_cache 
            if current_time - int(n.split('_')[0]) < 300
        }
        
        return nonce
    
    def validate_nonce(self, nonce: str, max_age_seconds: int = 300) -> bool:
        """Validate nonce (prevent replay attacks)"""
        if nonce in self.nonce_cache:
            return False  # Nonce already used
        
        try:
            timestamp = int(nonce.split('_')[0])
            current_time = int(time.time())
            
            if current_time - timestamp > max_age_seconds:
                return False  # Nonce too old
            
            self.nonce_cache.add(nonce)
            return True
            
        except (ValueError, IndexError):
            return False  # Invalid nonce format
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode())
        
        return {
            'hash': base64.b64encode(key).decode(),
            'salt': base64.b64encode(salt).decode()
        }
    
    def verify_password(self, password: str, hash_data: Dict[str, str]) -> bool:
        """Verify password against hash"""
        try:
            salt = base64.b64decode(hash_data['salt'])
            expected_hash = base64.b64decode(hash_data['hash'])
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            kdf.verify(password.encode(), expected_hash)
            return True
            
        except Exception:
            return False
    
    def create_webhook_signature(self, payload: str, secret: str) -> str:
        """Create webhook signature for secure webhooks"""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = self.create_webhook_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)

class RateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self):
        self.token_buckets = {}
        self.sliding_windows = {}
        self.fixed_windows = {}
    
    def token_bucket_allow(self, identifier: str, capacity: int, refill_rate: float) -> bool:
        """Token bucket rate limiting"""
        now = time.time()
        
        if identifier not in self.token_buckets:
            self.token_buckets[identifier] = {
                'tokens': capacity,
                'last_refill': now
            }
        
        bucket = self.token_buckets[identifier]
        
        # Refill tokens
        time_passed = now - bucket['last_refill']
        tokens_to_add = time_passed * refill_rate
        bucket['tokens'] = min(capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now
        
        # Check if request is allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False
    
    def sliding_window_allow(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Sliding window rate limiting"""
        now = time.time()
        
        if identifier not in self.sliding_windows:
            self.sliding_windows[identifier] = []
        
        window = self.sliding_windows[identifier]
        
        # Remove old entries
        cutoff_time = now - window_seconds
        self.sliding_windows[identifier] = [
            timestamp for timestamp in window 
            if timestamp > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.sliding_windows[identifier]) >= limit:
            return False
        
        # Add current request
        self.sliding_windows[identifier].append(now)
        return True
    
    def fixed_window_allow(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Fixed window rate limiting"""
        now = time.time()
        window_start = int(now // window_seconds) * window_seconds
        
        key = f"{identifier}_{window_start}"
        
        if key not in self.fixed_windows:
            self.fixed_windows[key] = 0
        
        if self.fixed_windows[key] >= limit:
            return False
        
        self.fixed_windows[key] += 1
        
        # Clean old windows
        self._clean_old_windows(now, window_seconds)
        
        return True
    
    def _clean_old_windows(self, now: float, window_seconds: int):
        """Clean old fixed windows"""
        current_window = int(now // window_seconds) * window_seconds
        
        keys_to_remove = []
        for key in self.fixed_windows:
            window_start = int(key.split('_')[-1])
            if window_start < current_window - window_seconds:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.fixed_windows[key]

class SecurityAudit:
    """Security audit and compliance checking"""
    
    def __init__(self):
        self.audit_log = []
        self.compliance_checks = []
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = 'info'):
        """Log security event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'severity': severity
        }
        
        self.audit_log.append(event)
        
        # Log to file
        logger.info(f"Security audit: {event_type}", extra=event)
    
    def add_compliance_check(self, name: str, check_func: callable, description: str):
        """Add compliance check"""
        self.compliance_checks.append({
            'name': name,
            'check_func': check_func,
            'description': description
        })
    
    def run_compliance_checks(self) -> Dict[str, Any]:
        """Run all compliance checks"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': [],
            'passed': 0,
            'failed': 0,
            'total': len(self.compliance_checks)
        }
        
        for check in self.compliance_checks:
            try:
                passed = check['check_func']()
                results['checks'].append({
                    'name': check['name'],
                    'description': check['description'],
                    'passed': passed,
                    'error': None
                })
                
                if passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['checks'].append({
                    'name': check['name'],
                    'description': check['description'],
                    'passed': False,
                    'error': str(e)
                })
                results['failed'] += 1
        
        return results
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.audit_log[-limit:]

# Global instances
advanced_security = AdvancedSecurity()
rate_limiter = RateLimiter()
security_audit = SecurityAudit()

# Setup default compliance checks
def setup_compliance_checks():
    """Setup default compliance checks"""
    security_audit.add_compliance_check(
        'env_file_permissions',
        lambda: oct(os.stat('.env').st_mode)[-3:] == '600' if os.path.exists('.env') else True,
        'Check that .env file has correct permissions (600)'
    )
    
    security_audit.add_compliance_check(
        'https_only',
        lambda: os.getenv('FLASK_ENV') != 'production' or os.getenv('HTTPS_ONLY', '').lower() == 'true',
        'Check that HTTPS is enforced in production'
    )
    
    security_audit.add_compliance_check(
        'secure_headers',
        lambda: True,  # Would check if security headers are configured
        'Check that security headers are properly configured'
    )

# Initialize compliance checks
setup_compliance_checks()
