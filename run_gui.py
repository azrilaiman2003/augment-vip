#!/usr/bin/env python3
"""
Simple launcher for Augment VIP GUI
This script checks dependencies and launches the GUI application
"""

import sys
import subprocess
import importlib.util

def check_and_install_dependencies():
    """Check if required packages are installed, install if missing"""
    required_packages = {
        'PyQt6': 'PyQt6',
        'psutil': 'psutil'
    }
    
    missing_packages = []
    
    for package_name, pip_name in required_packages.items():
        if importlib.util.find_spec(package_name) is None:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("Installing missing dependencies...")
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 Starting Augment VIP GUI...")
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install dependencies. Please install manually:")
        print("pip install PyQt6 psutil")
        sys.exit(1)
    
    # Import and run the GUI
    try:
        from gui_main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("Make sure gui_main.py and core_functions.py are in the same directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
