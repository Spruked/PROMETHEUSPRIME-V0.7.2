import requests
import json
import logging
import os
from typing import Union

logger = logging.getLogger(__name__)

def get_web3_storage_token():
    """Get Web3.Storage token from secure configuration"""
    try:
        from config.secure_config import config
        return config.web3_storage_token
    except ImportError:
        logger.warning("Secure config not available, using environment variable")
        token = os.getenv("WEB3_STORAGE_TOKEN")
        if not token:
            raise ValueError("WEB3_STORAGE_TOKEN not found in environment variables")
        return token

def upload_to_ipfs(json_metadata: Union[str, dict]) -> str:
    """
    Upload metadata to IPFS using Web3.Storage
    
    Args:
        json_metadata: JSON string or dictionary containing metadata
    
    Returns:
        IPFS URI (ipfs://...)
    
    Raises:
        ValueError: If token is missing or invalid
        Exception: If upload fails
    """
    try:
        # Get authentication token
        token = get_web3_storage_token()
        
        # Validate token format
        if not token or len(token) < 20:
            raise ValueError("Invalid Web3.Storage token")
        
        # Prepare metadata
        if isinstance(json_metadata, dict):
            metadata_json = json.dumps(json_metadata, indent=2)
        else:
            metadata_json = json_metadata
        
        # Validate JSON
        try:
            json.loads(metadata_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON metadata")
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Prepare files for upload
        files = {
            'file': ('metadata.json', metadata_json, 'application/json')
        }
        
        logger.info("Uploading metadata to IPFS...")
        
        # Make request to Web3.Storage
        response = requests.post(
            "https://api.web3.storage/upload",
            headers=headers,
            files=files,
            timeout=30
        )
        
        # Check response
        if response.status_code == 200:
            response_data = response.json()
            cid = response_data.get('cid')
            
            if not cid:
                raise Exception("No CID returned from Web3.Storage")
            
            ipfs_uri = f"ipfs://{cid}"
            logger.info(f"Successfully uploaded to IPFS: {ipfs_uri}")
            return ipfs_uri
            
        else:
            error_msg = f"IPFS upload failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f": {error_data.get('message', 'Unknown error')}"
            except:
                error_msg += f": {response.text}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during IPFS upload: {str(e)}")
        raise Exception(f"Network error: {str(e)}")
    
    except Exception as e:
        logger.error(f"IPFS upload failed: {str(e)}")
        raise

def verify_ipfs_upload(ipfs_uri: str) -> bool:
    """
    Verify that the uploaded content is accessible via IPFS
    
    Args:
        ipfs_uri: IPFS URI to verify
    
    Returns:
        True if accessible, False otherwise
    """
    try:
        if not ipfs_uri.startswith('ipfs://'):
            return False
        
        # Extract CID from URI
        cid = ipfs_uri[7:]  # Remove 'ipfs://' prefix
        
        # Try to access via public IPFS gateway
        gateway_url = f"https://ipfs.io/ipfs/{cid}"
        
        response = requests.head(gateway_url, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.warning(f"IPFS verification failed: {str(e)}")
        return False