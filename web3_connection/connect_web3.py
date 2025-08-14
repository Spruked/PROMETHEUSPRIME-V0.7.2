
from web3 import Web3
import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def get_web3_connection():
    config = load_config()
    rpc_url = config.get("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL is missing from config.json")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.isConnected():
        raise ConnectionError("Web3 provider is not connected.")
    return w3

def get_wallet_credentials():
    config = load_config()
    private_key = config.get("PRIVATE_KEY")
    account_address = config.get("ACCOUNT_ADDRESS")
    if not private_key or not account_address:
        raise ValueError("PRIVATE_KEY or ACCOUNT_ADDRESS is missing from config.json")
    return private_key, account_address