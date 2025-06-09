#!/usr/bin/env python3
"""
Installer script for Augment VIP

This script sets up a virtual environment and installs the Augment VIP package.
It works on Windows, macOS, and Linux with support for multiple IDEs.
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

# Console colors (basic version without colorama dependency)
if platform.system() == "Windows":
    # Windows doesn't support ANSI colors in all terminals
    BLUE = ""
    GREEN = ""
    YELLOW = ""
    RED = ""
    RESET = ""
else:
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"

def info(msg):
    """Print an info message"""
    print(f"{BLUE}[INFO]{RESET} {msg}")

def success(msg):
    """Print a success message"""
    print(f"{GREEN}[SUCCESS]{RESET} {msg}")

def warning(msg):
    """Print a warning message"""
    print(f"{YELLOW}[WARNING]{RESET} {msg}")

def error(msg):
    """Print an error message"""
    print(f"{RED}[ERROR]{RESET} {msg}")

def check_python_version():
    """Check if Python version is 3.6 or higher"""
    if sys.version_info < (3, 6):
        error("Python 3.6 or higher is required")
        sys.exit(1)

def create_venv(venv_path):
    """Create a virtual environment"""
    info(f"Creating virtual environment at {venv_path}...")

    try:
        import venv
        venv.create(venv_path, with_pip=True)
        success("Virtual environment created successfully")
        return True
    except Exception as e:
        error(f"Failed to create virtual environment: {e}")
        return False

def get_venv_python(venv_path):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def get_venv_pip(venv_path):
    """Get the path to the pip executable in the virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"

def install_package(venv_path, package_path="."):
    """Install the package in the virtual environment"""
    pip_path = get_venv_pip(venv_path)

    info(f"Installing Augment VIP package...")

    try:
        # Install the package in development mode
        subprocess.check_call([str(pip_path), "install", "-e", package_path])
        success("Augment VIP package installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to install package: {e}")
        return False

def run_command(venv_path, command_args):
    """Run a command in the virtual environment"""
    if platform.system() == "Windows":
        script_path = venv_path / "Scripts" / "augment-vip.exe"
    else:
        script_path = venv_path / "bin" / "augment-vip"

    if not script_path.exists():
        error(f"Command not found: augment-vip")
        return False

    try:
        full_command = [str(script_path)] + command_args
        subprocess.check_call(full_command)
        return True
    except subprocess.CalledProcessError as e:
        error(f"Command failed: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Install Augment VIP (Multi-IDE Version)")
    parser.add_argument("--clean", action="store_true", help="Run database cleaning on all detected IDEs after installation")
    parser.add_argument("--modify-ids", action="store_true", help="Run telemetry ID modification on all supported IDEs after installation")
    parser.add_argument("--all", action="store_true", help="Run all tools on all detected IDEs after installation")
    parser.add_argument("--no-prompt", action="store_true", help="Don't prompt for actions after installation")
    args = parser.parse_args()

    info("Starting installation process for Augment VIP (Multi-IDE Version)")

    # Check Python version
    check_python_version()

    # Determine the project root directory
    project_root = Path(__file__).resolve().parent

    # Create a virtual environment
    venv_path = project_root / ".venv"
    if not create_venv(venv_path):
        sys.exit(1)

    # Install the package
    if not install_package(venv_path, project_root):
        sys.exit(1)

    success("Installation completed successfully!")

    # Run commands if requested via command line arguments
    if args.clean or args.all:
        info("Running database cleaning on all detected IDEs...")
        run_command(venv_path, ["clean", "--auto"])

    if args.modify_ids or args.all:
        info("Running telemetry ID modification on all supported IDEs...")
        run_command(venv_path, ["modify-ids", "--auto"])

    # Print usage information
    if platform.system() == "Windows":
        cmd_path = f"{venv_path}\\Scripts\\augment-vip"
    else:
        cmd_path = f"{venv_path}/bin/augment-vip"

    print()
    print("=" * 60)
    print("                    USAGE INFORMATION")
    print("=" * 60)
    print()
    info("You can now use Augment VIP with the following commands:")
    print()
    info("List supported IDEs and their installation status:")
    info(f"  {cmd_path} list-ides")
    print()
    info("Clean databases (interactive IDE selection):")
    info(f"  {cmd_path} clean")
    print()
    info("Clean all detected IDEs automatically:")
    info(f"  {cmd_path} clean --auto")
    print()
    info("Clean specific IDE:")
    info(f"  {cmd_path} clean --ide vscode")
    info(f"  {cmd_path} clean --ide cursor")
    info(f"  {cmd_path} clean --ide intellij")
    print()
    info("Modify telemetry IDs (VS Code-based editors only):")
    info(f"  {cmd_path} modify-ids")
    info(f"  {cmd_path} modify-ids --auto")
    print()
    info("Run all operations:")
    info(f"  {cmd_path} all")
    info(f"  {cmd_path} all --auto")
    print()
    info("Supported IDEs:")
    info("  - VS Code, VS Code Insiders, Cursor, VSCodium (full support)")
    info("  - IntelliJ IDEA, PyCharm, WebStorm, PhpStorm (cleaning only)")
    print()

if __name__ == "__main__":
    main()
