"""
Utility functions for the Augment VIP project
"""

import os
import sys
import platform
import json
import sqlite3
import uuid
import shutil
import base64
import hashlib
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Console colors
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama for Windows support
    
    def info(msg: str) -> None:
        """Print an info message in blue"""
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")
    
    def success(msg: str) -> None:
        """Print a success message in green"""
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {msg}")
    
    def warning(msg: str) -> None:
        """Print a warning message in yellow"""
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}")
    
    def error(msg: str) -> None:
        """Print an error message in red"""
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")
        
except ImportError:
    # Fallback if colorama is not installed
    def info(msg: str) -> None:
        print(f"[INFO] {msg}")
    
    def success(msg: str) -> None:
        print(f"[SUCCESS] {msg}")
    
    def warning(msg: str) -> None:
        print(f"[WARNING] {msg}")
    
    def error(msg: str) -> None:
        print(f"[ERROR] {msg}")

def get_jetbrains_config_dir() -> Optional[Path]:
    """
    Find JetBrains configuration directory across different base directories.
    
    Returns:
        Path to JetBrains config directory if found, None otherwise
    """
    home_dir = Path.home()
    
    # Common base directories to check
    base_dirs = []
    
    if platform.system() == "Windows":
        # Windows paths
        if os.environ.get("APPDATA"):
            base_dirs.append(Path(os.environ["APPDATA"]))
        if os.environ.get("LOCALAPPDATA"):
            base_dirs.append(Path(os.environ["LOCALAPPDATA"]))
        base_dirs.append(home_dir)
    elif platform.system() == "Darwin":  # macOS
        base_dirs.extend([
            home_dir / "Library" / "Application Support",
            home_dir / "Library" / "Preferences",
            home_dir,
        ])
    else:  # Linux and other Unix-like systems
        base_dirs.extend([
            home_dir / ".config",
            home_dir / ".local" / "share",
            home_dir,
        ])
    
    # Look for JetBrains directory in each base directory
    for base_dir in base_dirs:
        if base_dir and base_dir.exists():
            jetbrains_dir = base_dir / "JetBrains"
            if jetbrains_dir.exists() and jetbrains_dir.is_dir():
                return jetbrains_dir
    
    return None

def get_vscode_files(machine_id_encoded: str) -> List[Path]:
    """
    Find VS Code configuration files across different variants and locations.
    
    Args:
        machine_id_encoded: Base64 encoded machine ID string
        
    Returns:
        List of paths to VS Code storage directories and files
    """
    home_dir = Path.home()
    vscode_dirs = []
    
    # Decode the machine ID
    try:
        machine_id = base64.b64decode(machine_id_encoded).decode('utf-8')
    except Exception:
        machine_id = "machineId"  # fallback
    
    # Common base directories to check
    base_dirs = []
    
    if platform.system() == "Windows":
        if os.environ.get("APPDATA"):
            base_dirs.append(Path(os.environ["APPDATA"]))
        if os.environ.get("LOCALAPPDATA"):
            base_dirs.append(Path(os.environ["LOCALAPPDATA"]))
        base_dirs.append(home_dir)
    elif platform.system() == "Darwin":  # macOS
        base_dirs.extend([
            home_dir / "Library" / "Application Support",
            home_dir,
        ])
    else:  # Linux
        base_dirs.extend([
            home_dir / ".config",
            home_dir / ".local" / "share",
            home_dir,
        ])
    
    # VS Code variant names to search for
    vscode_variants = [
        "Code", "Code - Insiders", "VSCodium", "code-server",
        "Cursor", "Windsurf", "Zed"
    ]
    
    for base_dir in base_dirs:
        if not base_dir or not base_dir.exists():
            continue
            
        # Look for VS Code variants in this base directory
        for entry in base_dir.iterdir():
            if entry.is_dir() and any(variant.lower() in entry.name.lower() for variant in vscode_variants):
                # Global storage patterns
                global_storage_paths = [
                    entry / "User" / "globalStorage",
                    entry / "data" / "User" / "globalStorage",
                    entry / machine_id,
                    entry / "data" / machine_id,
                ]
                
                for path in global_storage_paths:
                    if path.exists():
                        vscode_dirs.append(path)
                
                # Workspace storage patterns - enumerate all subdirectories
                workspace_storage_paths = [
                    entry / "User" / "workspaceStorage",
                    entry / "data" / "User" / "workspaceStorage",
                ]
                
                for workspace_base in workspace_storage_paths:
                    if workspace_base.exists():
                        for workspace_dir in workspace_base.iterdir():
                            if workspace_dir.is_dir():
                                vscode_dirs.append(workspace_dir)
    
    return [path for path in vscode_dirs if path.exists()]

def get_vscode_paths() -> Dict[str, Path]:
    """
    Get VS Code paths based on the operating system (legacy function for compatibility)
    
    Returns:
        Dict with paths to VS Code directories and files
    """
    system = platform.system()
    paths = {}
    
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            error("APPDATA environment variable not found")
            sys.exit(1)
        
        base_dir = Path(appdata) / "Code" / "User"
        
    elif system == "Darwin":  # macOS
        base_dir = Path.home() / "Library" / "Application Support" / "Code" / "User"
        
    elif system == "Linux":
        base_dir = Path.home() / ".config" / "Code" / "User"
        
    else:
        error(f"Unsupported operating system: {system}")
        sys.exit(1)
    
    # Common paths
    paths["base_dir"] = base_dir
    paths["storage_json"] = base_dir / "globalStorage" / "storage.json"
    paths["state_db"] = base_dir / "globalStorage" / "state.vscdb"
    
    return paths

def backup_file(file_path: Path) -> Path:
    """
    Create a backup of a file
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file
    """
    if not file_path.exists():
        error(f"File not found: {file_path}")
        sys.exit(1)
        
    backup_path = Path(f"{file_path}.backup")
    shutil.copy2(file_path, backup_path)
    success(f"Created backup at: {backup_path}")
    
    return backup_path

def generate_machine_id() -> str:
    """Generate a random 64-character hex string for machineId"""
    return uuid.uuid4().hex + uuid.uuid4().hex

def generate_device_id() -> str:
    """Generate a random UUID v4 for devDeviceId"""
    return str(uuid.uuid4())

def generate_sha256_hash() -> str:
    """Generate a SHA-256 hash of a new UUID"""
    return hashlib.sha256(uuid.uuid4().bytes).hexdigest()

def update_id_file(file_path: Path) -> bool:
    """
    Update an ID file with a new UUID.
    
    Args:
        file_path: Path to the ID file
        
    Returns:
        True if successful, False otherwise
    """
    info(f"Updating file: {file_path}")
    
    # Show old UUID if it exists
    if file_path.exists():
        try:
            old_uuid = file_path.read_text().strip()
            if old_uuid:
                info(f"Old UUID: {old_uuid}")
        except Exception:
            pass
    
    # Generate and show new UUID
    new_uuid = str(uuid.uuid4())
    info(f"New UUID: {new_uuid}")
    
    try:
        # Delete the file if it exists
        if file_path.exists():
            file_path.unlink()
        
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write new UUID to file
        file_path.write_text(new_uuid)
        
        success("Successfully wrote new UUID to file")
        return True
        
    except Exception as e:
        error(f"Failed to update ID file: {e}")
        return False

def lock_file(file_path: Path) -> bool:
    """
    Lock a file to make it read-only and protected.
    
    Args:
        file_path: Path to the file to lock
        
    Returns:
        True if successful, False otherwise
    """
    if not file_path.exists():
        error(f"File doesn't exist, can't lock: {file_path}")
        return False
    
    info(f"Locking file: {file_path}")
    
    try:
        # Use platform-specific commands to lock the file
        system = platform.system()
        
        if system == "Windows":
            import subprocess
            subprocess.run(["attrib", "+R", str(file_path)], check=False)
        else:
            import subprocess
            subprocess.run(["chmod", "444", str(file_path)], check=False)
            
            if system == "Darwin":  # macOS
                subprocess.run(["chflags", "uchg", str(file_path)], check=False)
        
        # Always ensure file is read-only using Python API
        import stat
        current_permissions = file_path.stat().st_mode
        new_permissions = current_permissions & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        file_path.chmod(new_permissions)
        
        success("Successfully locked file")
        return True
        
    except Exception as e:
        error(f"Failed to lock file: {e}")
        return False

def clean_vscode_database(vscode_path: Path, count_query: str, delete_query: str, 
                         file_name: str = "state.vscdb") -> bool:
    """
    Clean VS Code database by removing entries matching the query.
    
    Args:
        vscode_path: Path to VS Code storage directory
        count_query: SQL query to count entries to be deleted
        delete_query: SQL query to delete entries
        file_name: Database file name
        
    Returns:
        True if successful, False otherwise
    """
    state_db_path = vscode_path / file_name
    
    if not state_db_path.exists():
        return True
    
    try:
        conn = sqlite3.connect(str(state_db_path))
        cursor = conn.cursor()
        
        # Check how many rows would be deleted first
        cursor.execute(count_query)
        rows_to_delete = cursor.fetchone()[0]
        
        if rows_to_delete > 0:
            info(f"Found {rows_to_delete} potential entries to remove from '{state_db_path.name}'")
            
            # Execute the delete query
            cursor.execute(delete_query)
            conn.commit()
            
            success(f"Successfully removed {rows_to_delete} entries from '{state_db_path.name}'")
        
        conn.close()
        
        # Clean backup file if this isn't already a backup
        if not file_name.endswith(".backup"):
            backup_file_name = file_name + ".backup"
            clean_vscode_database(vscode_path, count_query, delete_query, backup_file_name)
        
        return True
        
    except Exception as e:
        error(f"Failed to clean database {state_db_path}: {e}")
        return False
