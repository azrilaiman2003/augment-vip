"""
Core functions for Augment VIP GUI
Simplified version without virtual environment complexity
"""

import os
import sys
import json
import sqlite3
import uuid
import shutil
import platform
import subprocess
import psutil
from pathlib import Path
from typing import Dict, Optional, Tuple


def get_vscode_paths() -> Dict[str, Path]:
    """Get VS Code paths based on the operating system"""
    system = platform.system()
    
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise Exception("APPDATA environment variable not found")
        base_dir = Path(appdata) / "Code" / "User"
        
    elif system == "Darwin":  # macOS
        base_dir = Path.home() / "Library" / "Application Support" / "Code" / "User"
        
    elif system == "Linux":
        base_dir = Path.home() / ".config" / "Code" / "User"
        
    else:
        raise Exception(f"Unsupported operating system: {system}")
    
    return {
        "base_dir": base_dir,
        "storage_json": base_dir / "globalStorage" / "storage.json",
        "state_db": base_dir / "globalStorage" / "state.vscdb"
    }


def backup_file(file_path: Path) -> Path:
    """Create a backup of a file"""
    if not file_path.exists():
        raise Exception(f"File not found: {file_path}")
        
    backup_path = Path(f"{file_path}.backup")
    shutil.copy2(file_path, backup_path)
    return backup_path


def generate_machine_id() -> str:
    """Generate a random 64-character hex string for machineId"""
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_device_id() -> str:
    """Generate a random UUID v4 for devDeviceId"""
    return str(uuid.uuid4())


def close_vscode() -> Tuple[bool, str]:
    """Close all VS Code processes"""
    try:
        closed_processes = []
        
        # Find and terminate VS Code processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if 'code' in proc_name and ('visual studio code' in proc_name or 
                                          proc_name in ['code.exe', 'code', 'code-insiders.exe', 'code-insiders']):
                    proc.terminate()
                    closed_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_processes:
            return True, f"Closed VS Code processes: {', '.join(set(closed_processes))}"
        else:
            return True, "No VS Code processes found running"
            
    except Exception as e:
        return False, f"Error closing VS Code: {str(e)}"


def clean_vscode_database() -> Tuple[bool, str]:
    """Clean VS Code databases by removing entries containing 'augment'"""
    try:
        paths = get_vscode_paths()
        state_db = paths["state_db"]
        
        if not state_db.exists():
            return False, f"VS Code database not found at: {state_db}"
        
        # Create backup
        backup_path = backup_file(state_db)
        
        # Connect to the database
        conn = sqlite3.connect(str(state_db))
        cursor = conn.cursor()
        
        # Get the count of records before deletion
        cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            conn.close()
            return True, "No Augment-related entries found in the database"
        
        # Delete records containing "augment"
        cursor.execute("DELETE FROM ItemTable WHERE key LIKE '%augment%'")
        conn.commit()
        
        # Get the count of records after deletion
        cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
        count_after = cursor.fetchone()[0]
        
        conn.close()
        
        removed_count = count_before - count_after
        return True, f"Successfully removed {removed_count} Augment-related entries from the database"
        
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def modify_telemetry_ids() -> Tuple[bool, str]:
    """Modify telemetry IDs in VS Code storage.json file"""
    try:
        paths = get_vscode_paths()
        storage_json = paths["storage_json"]
        
        if not storage_json.exists():
            return False, f"VS Code storage.json not found at: {storage_json}"
        
        # Create backup
        backup_path = backup_file(storage_json)
        
        # Generate new IDs
        machine_id = generate_machine_id()
        device_id = generate_device_id()
        
        # Read the current file
        with open(storage_json, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Update the values
        content["telemetry.machineId"] = machine_id
        content["telemetry.devDeviceId"] = device_id
        
        # Write the updated content back to the file
        with open(storage_json, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        return True, f"Successfully updated telemetry IDs\nNew machineId: {machine_id[:16]}...\nNew devDeviceId: {device_id}"
        
    except json.JSONDecodeError:
        return False, "The storage file is not valid JSON"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def run_all_operations() -> Tuple[bool, str]:
    """Run all operations: close VS Code, clean database, and modify IDs"""
    results = []
    overall_success = True
    
    # Close VS Code first
    success, message = close_vscode()
    results.append(f"Close VS Code: {message}")
    if not success:
        overall_success = False
    
    # Clean database
    success, message = clean_vscode_database()
    results.append(f"Clean Database: {message}")
    if not success:
        overall_success = False
    
    # Modify telemetry IDs
    success, message = modify_telemetry_ids()
    results.append(f"Modify IDs: {message}")
    if not success:
        overall_success = False
    
    return overall_success, "\n\n".join(results)
