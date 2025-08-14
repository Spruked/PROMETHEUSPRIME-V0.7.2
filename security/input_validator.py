from marshmallow import Schema, fields, validate, ValidationError as MarshmallowValidationError
from typing import Dict, Any, Optional
import re
import logging
# from security.input_validator import InputValidator

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """Secure input validation for NFT minting system"""
    
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Validate Ethereum address format"""
        if not address:
            return False
        
        # Remove 0x prefix if present
        if address.startswith('0x'):
            address = address[2:]
        
        # Check if it's 40 characters long and hexadecimal
        if len(address) != 40:
            return False
            
        try:
            int(address, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_ipfs_uri(uri: str) -> bool:
        """Validate IPFS URI format"""
        if not uri:
            return False
        
        # Check for valid IPFS URI format
        ipfs_pattern = r'^ipfs://[a-zA-Z0-9]{46,}$'
        return bool(re.match(ipfs_pattern, uri))
    
    @staticmethod
    def validate_private_key(private_key: str) -> bool:
        """Validate private key format (without logging the key)"""
        if not private_key:
            return False
        
        # Remove 0x prefix if present
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        
        # Check if it's 64 characters long and hexadecimal
        if len(private_key) != 64:
            return False
            
        try:
            int(private_key, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not input_string:
            return ""
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in input_string if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_metadata_fields(title: str, description: str, tags: list) -> Dict[str, Any]:
        """Validate NFT metadata fields"""
        errors = {}
        
        # Validate title
        if not title or len(title.strip()) < 3:
            errors['title'] = 'Title must be at least 3 characters long'
        elif len(title) > 100:
            errors['title'] = 'Title cannot exceed 100 characters'
        
        # Validate description
        if not description or len(description.strip()) < 10:
            errors['description'] = 'Description must be at least 10 characters long'
        elif len(description) > 2000:
            errors['description'] = 'Description cannot exceed 2000 characters'
        
        # Validate tags
        if not isinstance(tags, list):
            errors['tags'] = 'Tags must be a list'
        elif len(tags) > 10:
            errors['tags'] = 'Cannot have more than 10 tags'
        elif any(len(tag.strip()) < 2 for tag in tags if isinstance(tag, str)):
            errors['tags'] = 'Each tag must be at least 2 characters long'
        
        return errors

class NFTMintingSchema(Schema):
    """Schema for NFT minting request validation"""
    
    title = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=100),
            validate.Regexp(r'^[a-zA-Z0-9\s\-_\.]+$', error='Title contains invalid characters')
        ]
    )
    
    description = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=2000)
    )
    
    tags = fields.List(
        fields.Str(validate=validate.Length(min=2, max=50)),
        required=False,
      load_default=[],
        validate=validate.Length(max=10)
    )
    
    author = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        load_default=""
    )
    
    recipient_address = fields.Str(
        required=False,
        validate=validate.Length(equal=42)  # Ethereum address length
    )

def validate_nft_minting_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate NFT minting request data"""
    schema = NFTMintingSchema()
    
    try:
        # Validate and deserialize input
        validated_data = schema.load(data)
        
        # Additional custom validation
        validator = InputValidator()
        
        # Ensure validated_data is a dict
        if not isinstance(validated_data, dict):
            logger.error("Validated data is not a dictionary")
            raise ValidationError("Invalid input data format")
        
        # Sanitize string fields
        validated_data['title'] = validator.sanitize_string(validated_data.get('title', ''))
        validated_data['description'] = validator.sanitize_string(validated_data.get('description', ''))
        
        # Validate recipient address if provided
        if 'recipient_address' in validated_data and validated_data['recipient_address']:
            if not validator.validate_ethereum_address(validated_data['recipient_address']):
                raise ValidationError("Invalid Ethereum address format")
        
        # Validate metadata fields
        metadata_errors = validator.validate_metadata_fields(
            validated_data.get('title', ''),
            validated_data.get('description', ''),
            validated_data.get('tags', [])
        )
        
        if metadata_errors:
            raise ValidationError(f"Metadata validation failed: {metadata_errors}")
        
        return validated_data
        
    except MarshmallowValidationError as e:
        logger.error(f"Marshmallow validation error: {str(e)}")
        raise ValidationError(f"Schema validation failed: {str(e)}")
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected validation error: {str(e)}")
        raise ValidationError("Invalid input data")
