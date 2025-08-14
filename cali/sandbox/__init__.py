"""
CALI Sandbox Module
Provides secure execution environment for untrusted code and data processing
"""

import logging
import re
import ast
import types
from typing import Dict, Any, List, Optional, Union
from functools import wraps

logger = logging.getLogger("CALI.Sandbox")

# Safe built-in functions allowed in sandbox
SAFE_BUILTINS = {
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'chr', 'dict', 'dir',
    'divmod', 'enumerate', 'filter', 'float', 'format', 'hex', 'id',
    'int', 'len', 'list', 'map', 'max', 'min', 'oct', 'ord', 'pow',
    'range', 'repr', 'reversed', 'round', 'set', 'sorted', 'str',
    'sum', 'tuple', 'type', 'zip'
}

# Dangerous patterns to block
DANGEROUS_PATTERNS = [
    r'__.*__',  # Dunder methods
    r'eval\s*\(',  # eval calls
    r'exec\s*\(',  # exec calls
    r'import\s+',  # import statements
    r'from\s+.*\s+import',  # from imports
    r'open\s*\(',  # file operations
    r'file\s*\(',  # file operations
    r'subprocess',  # subprocess module
    r'os\.',  # os module calls
    r'sys\.',  # sys module calls
    r'globals\s*\(',  # globals access
    r'locals\s*\(',  # locals access
    r'vars\s*\(',  # vars access
    r'dir\s*\(',  # dir access to sensitive objects
]


class SandboxError(Exception):
    """Raised when sandbox security is violated"""
    pass


class CodeValidator:
    """Validates code for security before execution"""
    
    @staticmethod
    def validate_code(code: str) -> bool:
        """Check if code is safe to execute"""
        try:
            # Parse the code to AST
            tree = ast.parse(code)
            
            # Check for dangerous nodes
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    raise SandboxError("Import statements not allowed")
                
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id not in SAFE_BUILTINS:
                            raise SandboxError(f"Function '{node.func.id}' not allowed")
                
                if isinstance(node, ast.Attribute):
                    if node.attr.startswith('_'):
                        raise SandboxError("Private attributes not allowed")
            
            return True
            
        except SyntaxError as e:
            raise SandboxError(f"Syntax error: {e}")
    
    @staticmethod
    def validate_string(text: str) -> bool:
        """Check if string contains dangerous patterns"""
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False
        return True


class DataSandbox:
    """Sandbox for processing untrusted data"""
    
    def __init__(self, max_string_length: int = 10000, max_list_size: int = 1000):
        self.max_string_length = max_string_length
        self.max_list_size = max_list_size
        self.validator = CodeValidator()
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise SandboxError("Expected string input")
        
        if len(value) > self.max_string_length:
            raise SandboxError(f"String too long: {len(value)} > {self.max_string_length}")
        
        if not self.validator.validate_string(value):
            raise SandboxError("String contains dangerous patterns")
        
        # Basic HTML/JS sanitization
        dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'data:']
        for char in dangerous_chars:
            if char in value:
                value = value.replace(char, '')
        
        return value.strip()
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary data recursively"""
        if not isinstance(data, dict):
            raise SandboxError("Expected dictionary input")
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = self.sanitize_string(str(key))
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = self.sanitize_list(value)
            elif isinstance(value, (int, float, bool, type(None))):
                sanitized[clean_key] = value
            else:
                # Convert unknown types to string and sanitize
                sanitized[clean_key] = self.sanitize_string(str(value))
        
        return sanitized
    
    def sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitize list data"""
        if not isinstance(data, list):
            raise SandboxError("Expected list input")
        
        if len(data) > self.max_list_size:
            raise SandboxError(f"List too long: {len(data)} > {self.max_list_size}")
        
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            elif isinstance(item, (int, float, bool, type(None))):
                sanitized.append(item)
            else:
                sanitized.append(self.sanitize_string(str(item)))
        
        return sanitized


class ExecutionSandbox:
    """Sandbox for safe code execution"""
    
    def __init__(self):
        self.validator = CodeValidator()
        self.safe_globals = {
            '__builtins__': {name: __builtins__[name] for name in SAFE_BUILTINS if name in __builtins__}
        }
    
    def execute_safe(self, code: str, local_vars: Optional[Dict[str, Any]] = None) -> Any:
        """Execute code in a restricted environment"""
        if not self.validator.validate_code(code):
            raise SandboxError("Code validation failed")
        
        try:
            # Compile the code
            compiled_code = compile(code, '<sandbox>', 'eval')
            
            # Execute in restricted environment
            import ast
            # Use ast.literal_eval for safe evaluation if possible
            if isinstance(compiled_code, str):
                try:
                    result = ast.literal_eval(compiled_code)
                except Exception:
                    # Fallback to eval only if absolutely necessary (should be avoided)
                    result = eval(compiled_code, self.safe_globals, local_vars or {})
            else:
                # If not a string, fallback to eval (should be avoided)
                result = eval(compiled_code, self.safe_globals, local_vars or {})

            return result

        except Exception as e:
            raise SandboxError(f"Execution error: {e}")


def sandbox_decorator(func):
    """Decorator to apply sandboxing to function inputs"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        sandbox = DataSandbox()
        
        # Sanitize args
        sanitized_args = []
        for arg in args:
            if isinstance(arg, dict):
                sanitized_args.append(sandbox.sanitize_dict(arg))
            elif isinstance(arg, list):
                sanitized_args.append(sandbox.sanitize_list(arg))
            elif isinstance(arg, str):
                sanitized_args.append(sandbox.sanitize_string(arg))
            else:
                sanitized_args.append(arg)
        
        # Sanitize kwargs
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            clean_key = sandbox.sanitize_string(str(key))
            if isinstance(value, dict):
                sanitized_kwargs[clean_key] = sandbox.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_kwargs[clean_key] = sandbox.sanitize_list(value)
            elif isinstance(value, str):
                sanitized_kwargs[clean_key] = sandbox.sanitize_string(value)
            else:
                sanitized_kwargs[clean_key] = value
        
        return func(*sanitized_args, **sanitized_kwargs)
    
    return wrapper


# Create global sandbox instance
default_sandbox = DataSandbox()

def sanitize_input(data: Any) -> Any:
    """Convenient function to sanitize any input"""
    if isinstance(data, dict):
        return default_sandbox.sanitize_dict(data)
    elif isinstance(data, list):
        return default_sandbox.sanitize_list(data)
    elif isinstance(data, str):
        return default_sandbox.sanitize_string(data)
    else:
        return data
