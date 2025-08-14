import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any
from pythonjsonlogger import jsonlogger

class SecurityLogger:
    """Enhanced logging system for security events"""
    
    def __init__(self, app_name: str = "prometheus_nft", log_level: str = "INFO"):
        self.app_name = app_name
        self.log_level = getattr(logging, log_level.upper())
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(level=self.log_level)
        
        # Create formatters
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handlers
        self.setup_file_handlers(log_dir, json_formatter)
        
        # Setup console handler
        self.setup_console_handler(console_formatter)
        
        # Setup specific loggers
        self.setup_security_logger(log_dir, json_formatter)
        self.setup_transaction_logger(log_dir, json_formatter)
    
    def setup_file_handlers(self, log_dir: str, formatter):
        """Setup rotating file handlers"""
        # Main application log
        app_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setFormatter(formatter)
        app_handler.setLevel(logging.INFO)
        
        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Add handlers to root logger
        logging.getLogger().addHandler(app_handler)
        logging.getLogger().addHandler(error_handler)
    
    def setup_console_handler(self, formatter):
        """Setup console handler"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Only add console handler in development
        if os.getenv('FLASK_ENV') == 'development':
            logging.getLogger().addHandler(console_handler)
    
    def setup_security_logger(self, log_dir: str, formatter):
        """Setup dedicated security event logger"""
        security_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'security.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10  # Keep more security logs
        )
        security_handler.setFormatter(formatter)
        
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
    
    def setup_transaction_logger(self, log_dir: str, formatter):
        """Setup dedicated transaction logger"""
        tx_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'transactions.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=20  # Keep more transaction logs
        )
        tx_handler.setFormatter(formatter)
        
        tx_logger = logging.getLogger('transactions')
        tx_logger.addHandler(tx_handler)
        tx_logger.setLevel(logging.INFO)

class SecurityEventLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_failed_login(self, ip: str, user_agent: str = None, **kwargs):
        """Log failed login attempt"""
        self.logger.warning("Failed login attempt", extra={
            'event_type': 'failed_login',
            'ip_address': ip,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def log_blocked_ip(self, ip: str, reason: str, **kwargs):
        """Log IP blocking event"""
        self.logger.warning("IP blocked", extra={
            'event_type': 'ip_blocked',
            'ip_address': ip,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def log_suspicious_activity(self, activity_type: str, ip: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        self.logger.warning("Suspicious activity detected", extra={
            'event_type': 'suspicious_activity',
            'activity_type': activity_type,
            'ip_address': ip,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_security_config_change(self, change_type: str, details: Dict[str, Any]):
        """Log security configuration changes"""
        self.logger.info("Security configuration changed", extra={
            'event_type': 'config_change',
            'change_type': change_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_api_key_usage(self, api_key_hash: str, ip: str, endpoint: str, success: bool):
        """Log API key usage"""
        self.logger.info("API key usage", extra={
            'event_type': 'api_key_usage',
            'api_key_hash': api_key_hash,
            'ip_address': ip,
            'endpoint': endpoint,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        })

class TransactionLogger:
    """Specialized logger for blockchain transactions"""
    
    def __init__(self):
        self.logger = logging.getLogger('transactions')
    
    def log_mint_request(self, request_id: str, ip: str, metadata: Dict[str, Any]):
        """Log NFT mint request"""
        self.logger.info("NFT mint request", extra={
            'event_type': 'mint_request',
            'request_id': request_id,
            'ip_address': ip,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_mint_success(self, request_id: str, tx_hash: str, token_id: int, recipient: str):
        """Log successful NFT mint"""
        self.logger.info("NFT mint success", extra={
            'event_type': 'mint_success',
            'request_id': request_id,
            'transaction_hash': tx_hash,
            'token_id': token_id,
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_mint_failure(self, request_id: str, error: str, details: Dict[str, Any]):
        """Log failed NFT mint"""
        self.logger.error("NFT mint failed", extra={
            'event_type': 'mint_failure',
            'request_id': request_id,
            'error': error,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_ipfs_upload(self, request_id: str, cid: str, size: int):
        """Log IPFS upload"""
        self.logger.info("IPFS upload", extra={
            'event_type': 'ipfs_upload',
            'request_id': request_id,
            'cid': cid,
            'size': size,
            'timestamp': datetime.utcnow().isoformat()
        })

# Global logger instances
security_logger = SecurityEventLogger()
transaction_logger = TransactionLogger()

# Initialize logging system
def init_logging(app_name: str = "prometheus_nft", log_level: str = "INFO"):
    """Initialize the logging system"""
    return SecurityLogger(app_name, log_level)
