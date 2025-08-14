
# Prometheus Prime Documentation

This is the canonical README for the Prometheus Prime project. It merges the best content from previous versions and provides a clear overview for contributors and users.

## Overview
Prometheus Prime is a modular, extensible AI and blockchain platform designed for symbolic reasoning, emotional logging, and secure NFT minting. It integrates a FastAPI/Flask backend, a React dashboard frontend, and smart contract deployment tools.

## Key Features
- FastAPI/Flask backend for API endpoints and business logic
- React dashboard for real-time interaction
- NFT minting and contract deployment (Solidity, Hardhat)
- Emotional logging and symbolic recall modules (e.g., WhisperingArchive)
- Secure vault integration and advanced security middleware
- Modular architecture for easy extension

## Project Structure
- `core/` — Main backend logic, including FastAPI/Flask app, symbolic modules, and runtime extensions
- `ui/` — React frontend dashboard
- `contracts/` — Solidity smart contracts
- `contract_deployer/` — Hardhat and deployment scripts
- `vault_integration/` — Vault hooks and schema
- `security/`, `shield/` — Security, logging, and monitoring
- `minting_engine/` — NFT minting logic
- `ai_module/` — Metadata and AI extensions
- `archive/` — Legacy, backup, and notes (not part of runtime)

## Getting Started
1. **Python Environment:**
   - Use `venv311` (Python 3.11.x) as your virtual environment.
   - Install dependencies: `pip install -r requirements.txt`
2. **Frontend:**
   - Navigate to `ui/` and run `npm install` then `npm run dev`.
3. **Backend:**
   - Run the FastAPI/Flask app from `core/app.py` or `main.py`.
4. **Smart Contracts:**
   - Use Hardhat scripts in `contract_deployer/` for deployment.

## Contributing
- Please review the `docs/` folder for integration guides and architecture notes.
- Use the canonical `docs/README.md` for all future documentation updates.

## License
See LICENSE file for details.

---
This README supersedes all previous versions. For historical notes, see `archive/legacy/README_*.md`.

The dashboard will open automatically at http://localhost:5001

### 3. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Update the `.env` file with your actual values:
- Network RPC URL
- Wallet private key and address
- Web3.Storage token
- Contract address

### 4. Deploy Contract

```bash
cd contract_deployer
npm install
npx hardhat run scripts/deploy.js --network your-network
```

### 4. Run the Application

```bash
python app.py
```

## 🔧 API Endpoints

### Health Check
```
GET /health
```

### Mint NFT
```
POST /mint
Content-Type: application/json
X-API-Key: your-api-key

{
  "title": "Knowledge NFT Title",
  "description": "Detailed description of the knowledge",
  "tags": ["ai", "knowledge", "nft"],
  "author": "Author Name",
  "recipient_address": "0x..." (optional)
}
```

## 🛡️ Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use strong, unique API keys
- Rotate keys regularly
- Use different keys for different environments

### Network Security
- Use HTTPS in production
- Implement proper firewall rules
- Monitor for suspicious activity
- Keep dependencies updated

### Wallet Security
- Use hardware wallets for production
- Implement multi-signature wallets
- Never share private keys
- Use separate wallets for different purposes

## 📁 Project Structure

```
Alpha mint engine/
├── app.py                     # Main Flask application
├── security_setup.py          # Security configuration script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── ai_module/                # AI metadata generation
├── config/                   # Configuration management
│   └── secure_config.py      # Secure config loader
├── security/                 # Security modules
│   ├── input_validator.py    # Input validation
│   └── middleware.py         # Security middleware
├── minting_engine/           # NFT minting logic
├── ipfs_uploader/            # IPFS integration
├── contracts/                # Smart contracts
├── frontend/                 # React frontend
└── docs/                     # Documentation
```

## 🔍 Security Validation

The system includes comprehensive validation:

- **Input Sanitization**: All user inputs are sanitized
- **Address Validation**: Ethereum addresses are validated
- **Rate Limiting**: API endpoints are rate-limited
- **Authentication**: API key required for minting
- **Logging**: All requests and responses are logged

## 🚨 Security Warnings

⚠️ **Never commit sensitive data to version control**
⚠️ **Use different keys for development and production**
⚠️ **Regularly audit your security settings**
⚠️ **Monitor for unusual activity**

## 📊 Monitoring

The system logs:
- All API requests and responses
- Failed authentication attempts
- Blocked IP addresses
- Transaction details
- Error conditions

## 🔄 Updates and Maintenance

- Regularly update dependencies
- Monitor security advisories
- Review access logs
- Update API keys periodically
- Test backup and recovery procedures

## 🆘 Support

For security issues, please contact the development team immediately.

Created by Bryan Spruk. This is IP with teeth. 🔥

---

**Security Notice**: This system handles cryptocurrency transactions and sensitive data. Please review all security measures before deploying to production.