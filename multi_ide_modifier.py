#!/usr/bin/env python3
"""
Multi-IDE Telemetry ID Modifier

Python conversion of the Rust code for modifying telemetry IDs across multiple IDEs.
Supports JetBrains IDEs, VS Code variants, and other editors.

This is a standalone script equivalent to the Rust version.
"""

import os
import sys
import json
import base64
import sqlite3
import uuid
import hashlib
import shutil
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional

# Console colors
def setup_colors():
    """Setup console colors"""
    try:
        from colorama import init, Fore, Style
        init()
        return Fore, Style
    except ImportError:
        # Fallback without colors
        class MockColor:
            BLUE = GREEN = YELLOW = RED = ""
        class MockStyle:
            RESET_ALL = ""
        return MockColor(), MockStyle()

FORE, STYLE = setup_colors()

def info(msg: str) -> None:
    """Print an info message"""
    print(f"{FORE.BLUE}[INFO]{STYLE.RESET_ALL} {msg}")

def success(msg: str) -> None:
    """Print a success message"""
    print(f"{FORE.GREEN}[SUCCESS]{STYLE.RESET_ALL} {msg}")

def warning(msg: str) -> None:
    """Print a warning message"""
    print(f"{FORE.YELLOW}[WARNING]{STYLE.RESET_ALL} {msg}")

def error(msg: str) -> None:
    """Print an error message"""
    print(f"{FORE.RED}[ERROR]{STYLE.RESET_ALL} {msg}")

def get_jetbrains_config_dir() -> Optional[Path]:
    """
    Find JetBrains configuration directory across different base directories.
    
    Returns:
        Path to JetBrains config directory if found, None otherwise
    """
    home_dir = Path.home()
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
        machine_id = base64.b64decode(machine_id_encoded.encode()).decode('utf-8')
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
            
        try:
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
        except PermissionError:
            # Skip directories we can't read
            continue
    
    return [path for path in vscode_dirs if path.exists()]

def update_id_file(file_path: Path) -> bool:
    """
    Update an ID file with a new UUID.
    
    Args:
        file_path: Path to the ID file
        
    Returns:
        True if successful, False otherwise
    """
    print(f"Updating file: {file_path}")
    
    # Show old UUID if it exists
    if file_path.exists():
        try:
            old_uuid = file_path.read_text().strip()
            if old_uuid:
                print(f"Old UUID: {old_uuid}")
        except Exception:
            pass
    
    # Generate and show new UUID
    new_uuid = str(uuid.uuid4())
    print(f"New UUID: {new_uuid}")
    
    try:
        # Delete the file if it exists
        if file_path.exists():
            file_path.unlink()
        
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write new UUID to file
        file_path.write_text(new_uuid)
        
        print("Successfully wrote new UUID to file")
        return True
        
    except Exception as e:
        error(f"Failed to update ID file: {e}")
        return False

def update_vscode_files(vscode_file_path: Path, vscode_keys: List[str]) -> bool:
    """
    Update VS Code storage.json file with new telemetry IDs.
    
    Args:
        vscode_file_path: Path to VS Code storage directory
        vscode_keys: List of base64 encoded keys to update
        
    Returns:
        True if successful, False otherwise
    """
    storage_json_path = vscode_file_path / "storage.json"
    
    if storage_json_path.exists():
        print(f"Updating VSCode storage: {storage_json_path}")
        
        try:
            # Read existing storage.json or create empty object
            if storage_json_path.exists():
                with open(storage_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            for key_encoded in vscode_keys:
                try:
                    # Decode the key
                    key = base64.b64decode(key_encoded.encode()).decode('utf-8')
                    
                    # Show old value if it exists
                    if key in data:
                        print(f"Old UUID: {data[key]}")
                    
                    # Generate and update new value
                    if key_encoded == "dGVsZW1ldHJ5LmRldkRldmljZUlk":  # telemetry.devDeviceId
                        new_value = str(uuid.uuid4())
                    else:
                        # Some fields are SHA-256 hashes
                        new_value = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
                    
                    print(f"New UUID: {new_value}")
                    data[key] = new_value
                    
                except Exception as e:
                    error(f"Error processing key {key_encoded}: {e}")
                    continue
            
            # Write back to file
            with open(storage_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print("Successfully wrote new UUIDs to file")
            
        except Exception as e:
            error(f"Failed to update VS Code storage.json: {e}")
            return False
    
    # Handle direct ID files (if vscode_file_path is a file)
    if vscode_file_path.exists() and vscode_file_path.is_file():
        if update_id_file(vscode_file_path):
            return lock_file(vscode_file_path)
    
    return True

def clean_vscode_database(vscode_global_storage_path: Path, count_query: str, 
                         delete_query: str, file_name: str = "state.vscdb") -> bool:
    """
    Clean VS Code database by removing entries matching the query.
    
    Args:
        vscode_global_storage_path: Path to VS Code storage directory
        count_query: SQL query to count entries to be deleted
        delete_query: SQL query to delete entries
        file_name: Database file name
        
    Returns:
        True if successful, False otherwise
    """
    state_db_path = vscode_global_storage_path / file_name
    
    if not state_db_path.exists():
        return True
    
    try:
        conn = sqlite3.connect(str(state_db_path))
        cursor = conn.cursor()
        
        # Check how many rows would be deleted first
        cursor.execute(count_query)
        rows_to_delete = cursor.fetchone()[0]
        
        if rows_to_delete > 0:
            print(f"Found {rows_to_delete} potential entries to remove from '{state_db_path.name}'")
            
            # Execute the delete query
            cursor.execute(delete_query)
            conn.commit()
            
            print(f"Successfully removed {rows_to_delete} entries from '{state_db_path.name}'")
        
        conn.close()
        
        # Clean backup file if this isn't already a backup
        if not file_name.endswith(".backup"):
            backup_file_name = file_name + ".backup"
            clean_vscode_database(vscode_global_storage_path, count_query, delete_query, backup_file_name)
        
        return True
        
    except Exception as e:
        error(f"Failed to clean database {state_db_path}: {e}")
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
    
    print(f"Locking file: {file_path}")
    
    try:
        # Use platform-specific commands to lock the file
        system = platform.system()
        
        if system == "Windows":
            subprocess.run(["attrib", "+R", str(file_path)], check=False, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["chmod", "444", str(file_path)], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if system == "Darwin":  # macOS
                subprocess.run(["chflags", "uchg", str(file_path)], check=False,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Always ensure file is read-only using Python API
        import stat
        current_permissions = file_path.stat().st_mode
        new_permissions = current_permissions & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        file_path.chmod(new_permissions)
        
        print("Successfully locked file")
        return True
        
    except Exception as e:
        error(f"Failed to lock file: {e}")
        return False

def run() -> bool:
    """
    Main function that processes all supported IDEs.
    
    Returns:
        True if any programs were found and processed, False otherwise
    """
    programs_found = False
    
    # Try to find and update JetBrains
    jetbrains_dir = get_jetbrains_config_dir()
    if jetbrains_dir:
        programs_found = True
        
        # Base64 encoded filenames from Rust code
        id_files = ["UGVybWFuZW50RGV2aWNlSWQ=", "UGVybWFuZW50VXNlcklk"]
        
        for file_name_encoded in id_files:
            try:
                file_name = base64.b64decode(file_name_encoded.encode()).decode('utf-8')
                file_path = jetbrains_dir / file_name
                
                if update_id_file(file_path):
                    lock_file(file_path)
                    
            except Exception as e:
                error(f"Error processing JetBrains file {file_name_encoded}: {e}")
        
        print("JetBrains ID files have been updated and locked successfully!")
    else:
        print("JetBrains configuration directory not found")
    
    # Try to find and update VS Code variants
    machine_id_encoded = "bWFjaGluZUlk"  # machineId
    vscode_dirs = get_vscode_files(machine_id_encoded)
    
    if vscode_dirs:
        programs_found = True
        
        # Base64 encoded keys from Rust code
        vscode_keys = [
            "dGVsZW1ldHJ5Lm1hY2hpbmVJZA==",     # telemetry.machineId
            "dGVsZW1ldHJ5LmRldkRldmljZUlk",     # telemetry.devDeviceId
            "dGVsZW1ldHJ5Lm1hY01hY2hpbmVJZA=="  # telemetry.macMachineId
        ]
        
        # Database cleaning queries (base64 encoded)
        count_query_encoded = "U0VMRUNUIENPVU5UKCopIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw=="
        delete_query_encoded = "REVMRVRFIEZST00gSXRlbVRhYmxlIFdIRVJFIGtleSBMSUtFICclYXVnbWVudCUnOw=="
        
        try:
            count_query = base64.b64decode(count_query_encoded.encode()).decode('utf-8')
            delete_query = base64.b64decode(delete_query_encoded.encode()).decode('utf-8')
        except Exception as e:
            error(f"Failed to decode database queries: {e}")
            return False
        
        for vscode_dir in vscode_dirs:
            try:
                update_vscode_files(vscode_dir, vscode_keys)
                clean_vscode_database(vscode_dir, count_query, delete_query)
            except Exception as e:
                error(f"Error processing VS Code directory {vscode_dir}: {e}")
        
        print("All found VSCode variants' ID files have been updated and databases cleaned successfully!")
    else:
        print("No VSCode variants found")
    
    return programs_found

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Multi-IDE Telemetry ID Modifier")
        print("Usage: python multi_ide_modifier.py")
        print("\nSupported IDEs:")
        print("  - JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.)")
        print("  - VS Code variants (VS Code, VS Code Insiders, VSCodium, Cursor, etc.)")
        return
    
    try:
        if run():
            success("Multi-IDE telemetry ID modification completed successfully!")
        else:
            error("No JetBrains or VSCode installations found")
            sys.exit(1)
    except Exception as e:
        error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 