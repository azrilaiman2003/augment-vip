"""
IDE telemetry ID modification module
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from .utils import (
    info, success, error, warning, 
    get_ide_paths, backup_file, 
    generate_machine_id, generate_device_id
)

def modify_telemetry_ids() -> bool:
    """
    Modify VS Code telemetry IDs (legacy function for compatibility)
    
    Returns:
        True if successful, False otherwise
    """
    return modify_ide_telemetry_ids("vscode", None)

def modify_ide_telemetry_ids(ide_key: str, base_path: Path) -> bool:
    """
    Modify IDE telemetry IDs for VS Code-based editors
    
    Args:
        ide_key: IDE identifier key
        base_path: Base directory path for the IDE
        
    Returns:
        True if successful, False otherwise
    """
    if ide_key not in ["vscode", "vscode-insiders", "cursor", "codium"]:
        error(f"Telemetry ID modification not supported for {ide_key}")
        error("This operation is only supported for VS Code-based editors")
        return False
    
    info(f"Starting telemetry ID modification for {ide_key}")
    
    paths = get_ide_paths(ide_key, base_path)
    storage_json = paths.get("storage_json")
    
    if not storage_json or not storage_json.exists():
        warning(f"Storage file not found at: {storage_json}")
        return False
    
    info(f"Found storage file at: {storage_json}")
    
    backup_path = backup_file(storage_json)
    
    try:
        with open(storage_json, 'r', encoding='utf-8') as f:
            storage_data = json.load(f)
        
        new_machine_id = generate_machine_id()
        new_device_id = generate_device_id()
        
        old_machine_id = storage_data.get('machineId', 'Not found')
        old_device_id = storage_data.get('devDeviceId', 'Not found')
        
        storage_data['machineId'] = new_machine_id
        storage_data['devDeviceId'] = new_device_id
        
        with open(storage_json, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=2)
        
        success("Successfully modified telemetry IDs")
        info(f"Old Machine ID: {old_machine_id[:8]}...{old_machine_id[-8:] if len(old_machine_id) > 16 else old_machine_id}")
        info(f"New Machine ID: {new_machine_id[:8]}...{new_machine_id[-8:]}")
        info(f"Old Device ID: {old_device_id}")
        info(f"New Device ID: {new_device_id}")
        
        return True
        
    except json.JSONDecodeError as e:
        error(f"JSON parsing error: {e}")
        
        if backup_path.exists():
            info("Restoring from backup...")
            try:
                shutil.copy2(backup_path, storage_json)
                success("Restored from backup")
            except Exception as restore_error:
                error(f"Failed to restore from backup: {restore_error}")
        
        return False
    except Exception as e:
        error(f"Unexpected error: {e}")
        
        if backup_path and backup_path.exists():
            info("Restoring from backup...")
            try:
                shutil.copy2(backup_path, storage_json)
                success("Restored from backup")
            except Exception as restore_error:
                error(f"Failed to restore from backup: {restore_error}")
        
        return False
