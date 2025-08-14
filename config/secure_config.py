import os
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureConfig:
    """Secure configuration manager that loads from environment variables"""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize configuration from environment variables"""
        # Load environment variables from .env file
        load_dotenv(env_file)
        self._validate_required_vars()

    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are present"""
        required_vars = [
            'RPC_URL',
            'PRIVATE_KEY', 
            'ACCOUNT_ADDRESS',
            'WEB3_STORAGE_TOKEN',
            'CONTRACT_ADDRESS'
        ]
        # Explicitly declaring the type of the list resolves the type-checking warning
        missing_vars: list[str] = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value with optional default"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found and no default provided")
        return value

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default

    @property
    def network(self) -> str:
        return self.get('NETWORK', 'mainnet')

    @property
    def rpc_url(self) -> str:
        return self.get('RPC_URL')

    @property
    def private_key(self) -> str:
        key = self.get('PRIVATE_KEY')
        # Ensure private key starts with 0x
        if not key.startswith('0x'):
            key = '0x' + key
        return key

    @property
    def account_address(self) -> str:
        return self.get('ACCOUNT_ADDRESS')

    @property
    def web3_storage_token(self) -> str:
        return self.get('WEB3_STORAGE_TOKEN')

    @property
    def contract_address(self) -> str:
        return self.get('CONTRACT_ADDRESS')

    @property
    def flask_secret_key(self) -> str:
        # Note: This is an unused property in the current FastAPI app.
        return self.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

    @property
    def flask_env(self) -> str:
        # Renamed from FLASK_ENV to APP_ENV for clarity in a FastAPI context
        return self.get('FLASK_ENV', 'development')

    @property
    def database_url(self) -> str:
        # Note: This is an unused property in the current FastAPI app.
        return self.get('DATABASE_URL', 'sqlite:///app.db')

    @property
    def rate_limit_requests_per_minute(self) -> int:
        # Note: This is an unused property in the current FastAPI app.
        return self.get_int('RATE_LIMIT_REQUESTS_PER_MINUTE', 60)

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary (excluding sensitive data)"""
        return {
            'network': self.network,
            'rpc_url': self.rpc_url[:20] + "..." if len(self.rpc_url) > 20 else self.rpc_url,
            'account_address': self.account_address,
            'contract_address': self.contract_address,
            'flask_env': self.flask_env,
            'rate_limit_requests_per_minute': self.rate_limit_requests_per_minute
        }

# Global configuration instance
config = SecureConfig()
