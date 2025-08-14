#!/usr/bin/env python3
"""
System Status Check for Pro Prime Minting Alpha
Verifies all components are properly configured and ready for operation.
"""

import os
import sys
import json
import importlib.util
import subprocess  # nosec: B404
from pathlib import Path
from typing import Dict, List, Tuple, Any
import traceback

class SystemStatusChecker:
    """Comprehensive system status and health checker."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.getcwd())
        self.results = {
            'overall_status': 'UNKNOWN',
            'components': {},
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
    def check_all(self) -> Dict[str, Any]:
        """Run all system checks."""
        print("🔍 Running Pro Prime Minting Alpha System Check...")
        print("=" * 60)
        
        # Core system checks
        self._check_python_environment()
        self._check_dependencies()
        self._check_configuration()
        self._check_security_setup()
        self._check_dashboard_setup()
        self._check_contracts()
        self._check_api_endpoints()
        self._check_file_permissions()
        
        # Determine overall status
        self._determine_overall_status()
        
        # Print summary
        self._print_summary()
        
        return self.results
        
    def _check_python_environment(self):
        """Check Python version and environment."""
        print("🐍 Checking Python Environment...")
        
        try:
            python_version = sys.version_info
            if python_version.major == 3 and python_version.minor >= 8:
                self.results['components']['python'] = {
                    'status': 'OK',
                    'version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                    'message': 'Python version is compatible'
                }
                print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            else:
                self.results['components']['python'] = {
                    'status': 'ERROR',
                    'version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
                    'message': 'Python 3.8+ required'
                }
                print(f"   ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (3.8+ required)")
                
        except Exception as e:
            self.results['components']['python'] = {
                'status': 'ERROR',
                'message': f'Python check failed: {str(e)}'
            }
            print(f"   ❌ Python check failed: {str(e)}")
            
    def _check_dependencies(self):
        """Check if all required dependencies are installed."""
        print("📦 Checking Dependencies...")
        
        required_packages = [
            'flask', 'web3', 'requests', 'python-dotenv',
            'cryptography', 'flask-limiter', 'marshmallow',
            'flask-socketio', 'psutil', 'pyjwt'
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                installed_packages.append(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} - MISSING")
                
        if not missing_packages:
            self.results['components']['dependencies'] = {
                'status': 'OK',
                'installed': installed_packages,
                'message': 'All required dependencies installed'
            }
        else:
            self.results['components']['dependencies'] = {
                'status': 'ERROR',
                'installed': installed_packages,
                'missing': missing_packages,
                'message': f'Missing packages: {", ".join(missing_packages)}'
            }
            self.results['errors'].append(f'Missing dependencies: {", ".join(missing_packages)}')
            
    def _check_configuration(self):
        """Check configuration files."""
        print("⚙️  Checking Configuration...")
        
        config_files = [
            'config/config.json',
            'config/dashboard_config.json',
            'config/security_config.json',
            'config/monitoring_config.json'
        ]
        
        config_status = {'status': 'OK', 'files': {}}
        
        for config_file in config_files:
            file_path = self.base_dir / config_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    config_status['files'][config_file] = 'OK'
                    print(f"   ✅ {config_file}")
                except json.JSONDecodeError:
                    config_status['files'][config_file] = 'INVALID JSON'
                    config_status['status'] = 'WARNING'
                    print(f"   ⚠️  {config_file} - INVALID JSON")
            else:
                config_status['files'][config_file] = 'MISSING'
                config_status['status'] = 'WARNING'
                print(f"   ⚠️  {config_file} - MISSING")
                
        # Check .env file
        env_file = self.base_dir / '.env'
        if env_file.exists():
            config_status['files']['.env'] = 'OK'
            print(f"   ✅ .env")
        else:
            config_status['files']['.env'] = 'MISSING'
            config_status['status'] = 'WARNING'
            print(f"   ⚠️  .env - MISSING")
            self.results['warnings'].append('Environment file (.env) not found')
            
        self.results['components']['configuration'] = config_status
        
    def _check_security_setup(self):
        """Check security components."""
        print("🔒 Checking Security Setup...")
        
        security_components = [
            'security/input_validator.py',
            'security/rate_limiter.py',
            'security/encryption.py',
            'security/audit_logger.py',
            'security/compliance_checker.py'
        ]
        
        security_status = {'status': 'OK', 'components': {}}
        
        for component in security_components:
            file_path = self.base_dir / component
            if file_path.exists():
                security_status['components'][component] = 'OK'
                print(f"   ✅ {component}")
            else:
                security_status['components'][component] = 'MISSING'
                security_status['status'] = 'ERROR'
                print(f"   ❌ {component} - MISSING")
                
        self.results['components']['security'] = security_status
        
    def _check_dashboard_setup(self):
        """Check dashboard components."""
        print("📊 Checking Dashboard Setup...")
        
        dashboard_components = [
            'dashboard/app.py',
            'dashboard/templates/base.html',
            'dashboard/templates/dashboard.html',
            'dashboard/templates/monitoring.html',
            'dashboard/templates/config.html',
            'dashboard/templates/security.html',
            'start_dashboard.py'
        ]
        
        dashboard_status = {'status': 'OK', 'components': {}}
        
        for component in dashboard_components:
            file_path = self.base_dir / component
            if file_path.exists():
                dashboard_status['components'][component] = 'OK'
                print(f"   ✅ {component}")
            else:
                dashboard_status['components'][component] = 'MISSING'
                dashboard_status['status'] = 'ERROR'
                print(f"   ❌ {component} - MISSING")
                
        self.results['components']['dashboard'] = dashboard_status
        
    def _check_contracts(self):
        """Check smart contract files."""
        print("📜 Checking Smart Contracts...")
        
        contract_files = [
            'contracts/KnowledgeNFT.sol',
            'contracts/KnowledgeNFT_abi.json',
            'token_extensions/KnowledgeNFT_extended.sol'
        ]
        
        contract_status = {'status': 'OK', 'files': {}}
        
        for contract_file in contract_files:
            file_path = self.base_dir / contract_file
            if file_path.exists():
                contract_status['files'][contract_file] = 'OK'
                print(f"   ✅ {contract_file}")
            else:
                contract_status['files'][contract_file] = 'MISSING'
                contract_status['status'] = 'WARNING'
                print(f"   ⚠️  {contract_file} - MISSING")
                
        self.results['components']['contracts'] = contract_status
        
    def _check_api_endpoints(self):
        """Check API application files."""
        print("🌐 Checking API Components...")
        
        api_files = [
            'app.py',
            'minting_engine/mint_nft.py',
            'ai_module/metadata_generator.py',
            'ipfs_uploader/ipfs_upload.py',
            'web3_connection/connect_web3.py',
            'vault_integration/vault_trigger_hook.py'
        ]
        
        api_status = {'status': 'OK', 'files': {}}
        
        for api_file in api_files:
            file_path = self.base_dir / api_file
            if file_path.exists():
                api_status['files'][api_file] = 'OK'
                print(f"   ✅ {api_file}")
            else:
                api_status['files'][api_file] = 'MISSING'
                api_status['status'] = 'ERROR'
                print(f"   ❌ {api_file} - MISSING")
                
        self.results['components']['api'] = api_status
        
    def _check_file_permissions(self):
        """Check file permissions (Windows-specific)."""
        print("🔐 Checking File Permissions...")
        
        critical_files = [
            '.env',
            'config/config.json',
            'config/security_config.json'
        ]
        
        permissions_status = {'status': 'OK', 'files': {}}
        
        for file_name in critical_files:
            file_path = self.base_dir / file_name
            if file_path.exists():
                try:
                    # Check if file is readable
                    with open(file_path, 'r') as f:
                        f.read(1)
                    permissions_status['files'][file_name] = 'OK'
                    print(f"   ✅ {file_name}")
                except PermissionError:
                    permissions_status['files'][file_name] = 'PERMISSION DENIED'
                    permissions_status['status'] = 'ERROR'
                    print(f"   ❌ {file_name} - PERMISSION DENIED")
            else:
                permissions_status['files'][file_name] = 'NOT FOUND'
                print(f"   ⚠️  {file_name} - NOT FOUND")
                
        self.results['components']['permissions'] = permissions_status
        
    def _determine_overall_status(self):
        """Determine overall system status."""
        error_count = len(self.results['errors'])
        warning_count = len(self.results['warnings'])
        
        # Check component statuses
        error_components = []
        warning_components = []
        
        for component, status in self.results['components'].items():
            if status.get('status') == 'ERROR':
                error_components.append(component)
            elif status.get('status') == 'WARNING':
                warning_components.append(component)
                
        if error_components:
            self.results['overall_status'] = 'ERROR'
            self.results['errors'].extend([f'{comp} has errors' for comp in error_components])
        elif warning_components:
            self.results['overall_status'] = 'WARNING'
            self.results['warnings'].extend([f'{comp} has warnings' for comp in warning_components])
        else:
            self.results['overall_status'] = 'OK'
            
    def _print_summary(self):
        """Print summary of system status."""
        print("\n" + "=" * 60)
        print("📋 SYSTEM STATUS SUMMARY")
        print("=" * 60)
        
        status_emoji = {
            'OK': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌'
        }
        
        overall_status = self.results['overall_status']
        print(f"Overall Status: {status_emoji.get(overall_status, '❓')} {overall_status}")
        
        if self.results['errors']:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"   • {error}")
                
        if self.results['warnings']:
            print(f"\n⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
                
        # Component summary
        print(f"\n📊 Component Status:")
        for component, status in self.results['components'].items():
            status_str = status.get('status', 'UNKNOWN')
            emoji = status_emoji.get(status_str, '❓')
            print(f"   {emoji} {component.title()}: {status_str}")
            
        # Recommendations
        if overall_status != 'OK':
            print(f"\n💡 Recommendations:")
            
            if self.results['components'].get('dependencies', {}).get('status') == 'ERROR':
                print("   • Run: pip install -r requirements.txt")
                
            if self.results['components'].get('configuration', {}).get('status') == 'WARNING':
                print("   • Create missing configuration files")
                print("   • Copy .env.example to .env and configure")
                
            if self.results['components'].get('security', {}).get('status') == 'ERROR':
                print("   • Run: python security_setup.py setup")
                
            if self.results['components'].get('dashboard', {}).get('status') == 'ERROR':
                print("   • Verify dashboard components are properly created")
                
        print("\n" + "=" * 60)
        
        return self.results

def main():
    """Main function to run system status check."""
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.getcwd()
        
    checker = SystemStatusChecker(base_dir)
    results = checker.check_all()
    
    # Exit with appropriate code
    if results['overall_status'] == 'ERROR':
        sys.exit(1)
    elif results['overall_status'] == 'WARNING':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
