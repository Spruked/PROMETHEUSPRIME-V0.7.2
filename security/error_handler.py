import functools
import logging
import time
from typing import Callable, Any, Dict, Optional
from datetime import datetime, timedelta
import traceback
from web3.exceptions import Web3Exception
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class RetryableError(Exception):
    """Exception for errors that can be retried"""
    pass

class NonRetryableError(Exception):
    """Exception for errors that should not be retried"""
    pass

class ErrorHandler:
    """Centralized error handling and recovery system"""
    
    def __init__(self):
        self.error_counts = {}
        self.circuit_breakers = {}
    
    def record_error(self, error_type: str, component: str):
        """Record an error for monitoring"""
        key = f"{component}.{error_type}"
        if key not in self.error_counts:
            self.error_counts[key] = {
                'count': 0,
                'first_occurrence': datetime.now(),
                'last_occurrence': datetime.now()
            }
        
        self.error_counts[key]['count'] += 1
        self.error_counts[key]['last_occurrence'] = datetime.now()
        
        # Log the error
        logger.error(f"Error recorded: {key}", extra={
            'error_type': error_type,
            'component': component,
            'count': self.error_counts[key]['count']
        })
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.error_counts.copy()
    
    def should_circuit_break(self, component: str, threshold: int = 5, window_minutes: int = 5) -> bool:
        """Check if circuit breaker should be triggered"""
        if component not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[component]
        
        # Check if we're in the failure window
        if datetime.now() - breaker['last_failure'] > timedelta(minutes=window_minutes):
            # Reset the breaker if window has passed
            breaker['failure_count'] = 0
            return False
        
        return breaker['failure_count'] >= threshold
    
    def trigger_circuit_breaker(self, component: str):
        """Trigger circuit breaker for a component"""
        if component not in self.circuit_breakers:
            self.circuit_breakers[component] = {
                'failure_count': 0,
                'last_failure': datetime.now(),
                'is_open': False
            }
        
        breaker = self.circuit_breakers[component]
        breaker['failure_count'] += 1
        breaker['last_failure'] = datetime.now()
        breaker['is_open'] = self.should_circuit_break(component)
        
        if breaker['is_open']:
            logger.critical(f"Circuit breaker opened for {component}")

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple = (RetryableError, Web3Exception, RequestException)
):
    """Decorator for retrying functions with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                
                except Exception as e:
                    # Non-retryable error
                    logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
                    raise
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def handle_web3_errors(func: Callable) -> Callable:
    """Decorator to handle Web3 specific errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except Web3Exception as e:
            error_msg = str(e)
            
            # Classify Web3 errors
            if 'insufficient funds' in error_msg.lower():
                raise NonRetryableError(f"Insufficient funds: {error_msg}")
            
            elif 'nonce too low' in error_msg.lower():
                raise RetryableError(f"Nonce too low, retrying: {error_msg}")
            
            elif 'gas' in error_msg.lower():
                raise RetryableError(f"Gas related error: {error_msg}")
            
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                raise RetryableError(f"Network error: {error_msg}")
            
            else:
                # Unknown Web3 error, don't retry
                raise NonRetryableError(f"Unknown Web3 error: {error_msg}")
        
        except Exception as e:
            # Re-raise non-Web3 exceptions
            raise
    
    return wrapper

def handle_ipfs_errors(func: Callable) -> Callable:
    """Decorator to handle IPFS specific errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except RequestException as e:
            error_msg = str(e)
            
            # Classify IPFS errors
            if hasattr(e, 'response') and e.response:
                status_code = e.response.status_code
                
                if status_code == 429:
                    raise RetryableError(f"Rate limit exceeded: {error_msg}")
                
                elif status_code >= 500:
                    raise RetryableError(f"Server error: {error_msg}")
                
                elif status_code == 401:
                    raise NonRetryableError(f"Authentication failed: {error_msg}")
                
                elif status_code == 413:
                    raise NonRetryableError(f"Payload too large: {error_msg}")
                
                else:
                    raise NonRetryableError(f"Client error: {error_msg}")
            
            else:
                # Network related error
                raise RetryableError(f"Network error: {error_msg}")
        
        except Exception as e:
            # Re-raise non-IPFS exceptions
            raise
    
    return wrapper

def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute a function and return structured result"""
    start_time = time.time()
    result = {
        'success': False,
        'data': None,
        'error': None,
        'execution_time': 0,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        result['data'] = func(*args, **kwargs)
        result['success'] = True
        
    except Exception as e:
        result['error'] = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        
        # Log the error
        logger.error(f"Error executing {func.__name__}: {str(e)}", extra={
            'function': func.__name__,
            'args': str(args)[:100],  # Limit length
            'kwargs': str(kwargs)[:100],  # Limit length
            'traceback': traceback.format_exc()
        })
    
    finally:
        result['execution_time'] = time.time() - start_time
    
    return result

def create_health_check():
    """Create a health check function for the system"""
    
    def health_check() -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'components': {},
            'errors': []
        }
        
        # Check Web3 connection
        try:
            from config.secure_config import config
            from web3 import Web3
            
            w3 = Web3(Web3.HTTPProvider(config.rpc_url))
            is_connected = w3.is_connected()
            
            health_status['components']['web3'] = {
                'status': 'healthy' if is_connected else 'unhealthy',
                'connected': is_connected,
                'network': config.network
            }
            
            if not is_connected:
                health_status['errors'].append('Web3 connection failed')
        
        except Exception as e:
            health_status['components']['web3'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['errors'].append(f'Web3 check failed: {str(e)}')
        
        # Check IPFS connectivity
        try:
            import requests
            response = requests.get('https://api.web3.storage/user/uploads?size=1', timeout=10)
            ipfs_healthy = response.status_code in [200, 401]  # 401 means service is up but auth failed
            
            health_status['components']['ipfs'] = {
                'status': 'healthy' if ipfs_healthy else 'unhealthy',
                'response_code': response.status_code
            }
            
            if not ipfs_healthy:
                health_status['errors'].append('IPFS service unhealthy')
        
        except Exception as e:
            health_status['components']['ipfs'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['errors'].append(f'IPFS check failed: {str(e)}')
        
        # Check database connectivity (if applicable)
        try:
            # Add database check here if you have a database
            health_status['components']['database'] = {
                'status': 'not_configured'
            }
        except Exception as e:
            health_status['components']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['errors'].append(f'Database check failed: {str(e)}')
        
        # Overall health status
        if health_status['errors']:
            health_status['status'] = 'unhealthy'
        
        return health_status
    
    return health_check

# Global error handler instance
error_handler = ErrorHandler()

# Health check function
health_check = create_health_check()
