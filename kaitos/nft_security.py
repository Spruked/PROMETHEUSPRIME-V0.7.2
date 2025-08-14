#!/usr/bin/env python3
"""
Security setup script for Prometheus NFT Minting Engine
This script helps set up secure configuration and validates security settings.
"""

import os
import sys
import secrets
import getpass
from pathlib import Path

def generate_secure_key():
    """Generate a secure random key"""
    return secrets.token_urlsafe(32)

def get_env_file_path():
    """Get the path to the .env file"""
    return Path(__file__).parent / '.env'

def create_env_file():
    """Create .env file with secure defaults"""
    env_file = get_env_file_path()
    
    if env_file.exists():
        response = input(f".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    print("Setting up secure environment configuration...")
    print("Please provide the following information:")
    
    # Network configuration
    print("\n=== Network Configuration ===")
    network = input("Network (mainnet/sepolia/polygon): ").strip() or "mainnet"
    rpc_url = input("RPC URL: ").strip()
    
    # Wallet configuration
    print("\n=== Wallet Configuration ===")
    print("WARNING: Never share your private key!")
    private_key = getpass.getpass("Private Key (hidden): ").strip()
    account_address = input("Account Address: ").strip()
    
    # Contract configuration
    print("\n=== Contract Configuration ===")
    contract_address = input("Contract Address: ").strip()
    
    # IPFS configuration
    print("\n=== IPFS Configuration ===")
    web3_storage_token = getpass.getpass("Web3.Storage Token (hidden): ").strip()
    
    # Generate secure keys
    flask_secret_key = generate_secure_key()
    api_key = generate_secure_key()
    
    # Create .env content
    env_content = f"""# Network Configuration
NETWORK={network}
RPC_URL={rpc_url}

# Wallet Configuration (NEVER commit actual private keys)
PRIVATE_KEY={private_key}
ACCOUNT_ADDRESS={account_address}

# IPFS Configuration
WEB3_STORAGE_TOKEN={web3_storage_token}

# Contract Configuration
CONTRACT_ADDRESS={contract_address}

# Flask Configuration
FLASK_SECRET_KEY={flask_secret_key}
FLASK_ENV=development

# API Security
API_KEY={api_key}

# Database Configuration (if needed)
DATABASE_URL=sqlite:///app.db

# API Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
"""
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Set secure permissions
    os.chmod(env_file, 0o600)
    
    print(f"\n✅ Environment file created: {env_file}")
    print(f"✅ Generated API Key: {api_key}")
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Never commit the .env file to version control")
    print("2. Keep your private key secure and never share it")
    print("3. Use the generated API key for authenticated requests")
    print("4. Review all configuration values before running in production")

def validate_security_settings():
    """Validate security settings"""
    print("\n=== Security Validation ===")
    
    env_file = get_env_file_path()
    if not env_file.exists():
        print("❌ .env file not found. Run setup first.")
        return False
    
    # Check file permissions
    file_perms = oct(os.stat(env_file).st_mode)[-3:]
    if file_perms != '600':
        print(f"⚠️  Warning: .env file permissions are {file_perms}, should be 600")
        print("   Run: chmod 600 .env")
    
    # Load and validate environment variables
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    required_vars = [
        'NETWORK', 'RPC_URL', 'PRIVATE_KEY', 'ACCOUNT_ADDRESS',
        'WEB3_STORAGE_TOKEN', 'CONTRACT_ADDRESS', 'FLASK_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Validate private key format
    private_key = os.getenv('PRIVATE_KEY')
    if private_key:
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        if len(private_key) != 66:
            print("❌ Invalid private key format")
            return False
    
    # Validate Ethereum address format
    account_address = os.getenv('ACCOUNT_ADDRESS')
    if account_address and (not account_address.startswith('0x') or len(account_address) != 42):
        print("❌ Invalid account address format")
        return False
    
    # Check for default values
        flask_secret = os.getenv('FLASK_SECRET_KEY')
        if not flask_secret:
            print("⚠️  Warning: FLASK_SECRET_KEY environment variable is not set!")
    
    print("✅ Security validation passed")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n=== Dependency Check ===")
    
    required_packages = [
        'flask', 'web3', 'requests', 'python-dotenv', 
        'flask-limiter', 'marshmallow', 'cryptography'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main setup function"""
    print("🔒 Prometheus NFT Minting Engine - Security Setup")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python security_setup.py setup    - Create .env file")
        print("  python security_setup.py validate - Validate security settings")
        print("  python security_setup.py check    - Check dependencies")
        return
    
    command = sys.argv[1]
    
    if command == 'setup':
        create_env_file()
    elif command == 'validate':
        validate_security_settings()
    elif command == 'check':
        check_dependencies()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
