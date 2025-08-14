from web3 import Web3
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from secure config module"""
    try:
        from config.secure_config import config
        return config
    except ImportError:
        logger.error("Failed to import secure config. Using fallback configuration.")
        # Fallback to environment variables
        return {
            "RPC_URL": os.getenv("RPC_URL"),
            "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
            "ACCOUNT_ADDRESS": os.getenv("ACCOUNT_ADDRESS"),
            "CONTRACT_ADDRESS": os.getenv("CONTRACT_ADDRESS")
        }

def validate_transaction_params(metadata_uri: str, recipient_address: Optional[str] = None) -> dict:
    """Validate transaction parameters before minting"""
    errors = {}
    
    if not metadata_uri:
        errors['metadata_uri'] = 'Metadata URI is required'
    elif not metadata_uri.startswith('ipfs://'):
        errors['metadata_uri'] = 'Invalid IPFS URI format'
    
    if recipient_address:
        if not Web3.is_address(recipient_address):
            errors['recipient_address'] = 'Invalid Ethereum address'
    
    return errors

def mint_nft(metadata_uri: str, recipient_address: Optional[str] = None):
    """
    Mint an NFT with the given metadata URI
    
    Args:
        metadata_uri: IPFS URI of the metadata
        recipient_address: Optional recipient address (defaults to account address)
    
    Returns:
        Transaction receipt
    
    Raises:
        ValueError: If validation fails
        Exception: If transaction fails
    """
    try:
        # Load configuration
        config = load_config()
        
        # Validate inputs
        validation_errors = validate_transaction_params(metadata_uri, recipient_address)
        if validation_errors:
            raise ValueError(f"Validation errors: {validation_errors}")
        
        # Get configuration values
        if hasattr(config, 'rpc_url'):
            # Using secure config object
            rpc_url = config.rpc_url
            private_key = config.private_key
            account_address = config.account_address
            contract_address = config.contract_address
        else:
            # Using fallback dict
            rpc_url = config.get("RPC_URL")
            private_key = config.get("PRIVATE_KEY")
            account_address = config.get("ACCOUNT_ADDRESS")
            contract_address = config.get("CONTRACT_ADDRESS")
        
        # Use recipient address or default to account address
        recipient = recipient_address or account_address
        
        # Validate required configuration
        if not all([rpc_url, private_key, account_address, contract_address]):
            raise ValueError("Missing required configuration values")
        
        # Initialize Web3 connection
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain network")
        
        logger.info("Connected to blockchain network")
        
        # Load contract ABI
        abi_path = os.path.join(os.path.dirname(__file__), '../contracts/KnowledgeNFT_abi.json')
        
        if not os.path.exists(abi_path):
            raise FileNotFoundError(f"Contract ABI not found at {abi_path}")
        
        with open(abi_path, "r") as abi_file:
            abi = json.load(abi_file)
        
        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(contract_address), 
            abi=abi
        )
        
        # Get transaction parameters
        nonce = w3.eth.get_transaction_count(account_address)
        
        # Estimate gas
        try:
            gas_estimate = contract.functions.mintKnowledgeNFT(
                Web3.to_checksum_address(recipient), 
                metadata_uri
            ).estimate_gas({'from': account_address})
            
            # Add 20% buffer for gas estimation
            gas_limit = int(gas_estimate * 1.2)
            
        except Exception as e:
            logger.warning(f"Gas estimation failed: {str(e)}, using default gas limit")
            gas_limit = 300000
        
        # Get current gas price
        gas_price = w3.eth.gas_price
        
        # Build transaction
        txn = contract.functions.mintKnowledgeNFT(
            Web3.to_checksum_address(recipient), 
            metadata_uri
        ).build_transaction({
            'from': account_address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price
        })
        
        logger.info(f"Minting NFT to {recipient} with URI: {metadata_uri}")
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        logger.info(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if tx_receipt.status == 1:
            logger.info(f"NFT minted successfully! Transaction: {tx_hash.hex()}")
        else:
            logger.error(f"Transaction failed: {tx_hash.hex()}")
            raise Exception("Transaction failed")
        
        return tx_receipt
        
    except Exception as e:
        logger.error(f"Minting failed: {str(e)}")
        raise