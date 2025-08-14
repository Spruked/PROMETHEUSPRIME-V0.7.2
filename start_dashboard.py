#!/usr/bin/env python3
"""
Dashboard startup script for Prometheus NFT Minting Engine
"""

import os
import sys
import time
import subprocess  # nosec: B404
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardManager:
    """Manage the dashboard application"""
    
    def __init__(self):
        self.dashboard_port = 5001
        self.api_port = 5000
        self.dashboard_process = None
        self.api_process = None
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        required_packages = [
            'flask', 'flask-socketio', 'python-socketio', 'eventlet'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing required packages: {', '.join(missing_packages)}")
            logger.info("Install with: pip install flask flask-socketio python-socketio eventlet")
            return False
        
        return True
    
    def check_ports(self):
        """Check if ports are available"""
        import socket
        
        def is_port_available(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0
        
        if not is_port_available(self.dashboard_port):
            logger.error(f"Port {self.dashboard_port} is already in use")
            return False
        
        if not is_port_available(self.api_port):
            logger.warning(f"Port {self.api_port} is already in use (main API)")
        
        return True
    
    def start_dashboard(self, host='127.0.0.1', debug=False):
        """Start the dashboard application"""
        logger.info(f"Starting dashboard on {host}:{self.dashboard_port}")
        
        try:
            # Import and start dashboard
            from dashboard.app import dashboard_app
            dashboard_app.run(host=host, port=self.dashboard_port, debug=debug)
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {str(e)}")
            return False
        
        return True
    
    def start_api(self, host='127.0.0.1', debug=False):
        """Start the main API application"""
        logger.info(f"Starting API on {host}:{self.api_port}")
        
        try:
            # Import and start main API
            from app import app
            app.run(host=host, port=self.api_port, debug=debug, threaded=True)
            
        except Exception as e:
            logger.error(f"Failed to start API: {str(e)}")
            return False
        
        return True
    
    def start_both(self, host='127.0.0.1', debug=False):
        """Start both dashboard and API in separate processes"""
        import multiprocessing
        
        logger.info("Starting both dashboard and API applications")
        
        # Start API process
        api_process = multiprocessing.Process(
            target=self.start_api,
            args=(host, debug)
        )
        api_process.start()
        
        # Wait a moment for API to start
        time.sleep(2)
        
        # Start dashboard process
        dashboard_process = multiprocessing.Process(
            target=self.start_dashboard,
            args=(host, debug)
        )
        dashboard_process.start()
        
        try:
            # Wait for both processes
            api_process.join()
            dashboard_process.join()
        except KeyboardInterrupt:
            logger.info("Shutting down applications...")
            api_process.terminate()
            dashboard_process.terminate()
            api_process.join()
            dashboard_process.join()
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for easy access"""
        if sys.platform == 'win32':
            try:
                import winshell
                from win32com.client import Dispatch
                
                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, 'Prometheus NFT Dashboard.lnk')
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = 'http://127.0.0.1:5001'
                shortcut.IconLocation = sys.executable
                shortcut.save()
                
                logger.info(f"Desktop shortcut created: {shortcut_path}")
                
            except ImportError:
                logger.warning("Could not create desktop shortcut (winshell not installed)")
            except Exception as e:
                logger.error(f"Failed to create desktop shortcut: {str(e)}")
    
    def open_browser(self):
        """Open browser to dashboard"""
        import webbrowser
        url = f"http://127.0.0.1:{self.dashboard_port}"
        
        logger.info(f"Opening browser to {url}")
        webbrowser.open(url)
    
    def show_access_info(self):
        """Show access information"""
        print("\n" + "="*60)
        print("🔥 PROMETHEUS NFT MINTING ENGINE DASHBOARD")
        print("="*60)
        print(f"Dashboard URL: http://127.0.0.1:{self.dashboard_port}")
        print(f"API URL:       http://127.0.0.1:{self.api_port}")
        print("")
        print("Available Pages:")
        print("  • Dashboard:    /")
        print("  • Monitoring:   /monitoring")
        print("  • Security:     /security")
        print("  • Transactions: /transactions")
        print("  • Logs:         /logs")
        print("  • Config:       /config")
        print("")
        print("API Endpoints:")
        print("  • Health:       /health")
        print("  • Metrics:      /metrics")
        print("  • Mint NFT:     /mint")
        print("  • Audit:        /security/audit")
        print("="*60)
        print("Press Ctrl+C to stop\n")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Prometheus NFT Minting Engine Dashboard'
    )
    
    parser.add_argument(
        '--mode', 
        choices=['dashboard', 'api', 'both'],
        default='dashboard',
        help='Which application to start'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    
    parser.add_argument(
        '--create-shortcut',
        action='store_true',
        help='Create desktop shortcut'
    )
    
    args = parser.parse_args()
    
    # Create dashboard manager
    manager = DashboardManager()
    
    # Check dependencies
    if not manager.check_dependencies():
        sys.exit(1)
    
    # Check ports
    if not manager.check_ports():
        sys.exit(1)
    
    # Create desktop shortcut if requested
    if args.create_shortcut:
        manager.create_desktop_shortcut()
    
    # Show access information
    manager.show_access_info()
    
    # Open browser if not disabled
    if not args.no_browser and args.mode in ['dashboard', 'both']:
        # Delay browser opening to allow server to start
        import threading
        def delayed_browser():
            time.sleep(3)
            manager.open_browser()
        
        browser_thread = threading.Thread(target=delayed_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # Start the requested application(s)
    try:
        if args.mode == 'dashboard':
            manager.start_dashboard(args.host, args.debug)
        elif args.mode == 'api':
            manager.start_api(args.host, args.debug)
        elif args.mode == 'both':
            manager.start_both(args.host, args.debug)
    
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
