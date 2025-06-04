"""
Multi-IDE telemetry ID modifier module

Supports VS Code variants, JetBrains IDEs, and other editors
"""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List

from .utils import (
    info, success, error, warning, 
    get_jetbrains_config_dir, get_vscode_files,
    update_id_file, lock_file, clean_vscode_database,
    generate_machine_id, generate_device_id, generate_sha256_hash
)

def modify_jetbrains_ids() -> bool:
    """
    Modify JetBrains telemetry IDs by updating permanent device and user ID files.
    
    Returns:
        True if successful, False otherwise
    """
    info("Starting JetBrains telemetry ID modification")
    
    jetbrains_dir = get_jetbrains_config_dir()
    if not jetbrains_dir:
        warning("JetBrains configuration directory not found")
        return False
    
    info(f"Found JetBrains config directory at: {jetbrains_dir}")
    
    # Base64 encoded filenames from Rust code
    id_files_encoded = [
        "UGVybWFuZW50RGV2aWNlSWQ=",  # PermanentDeviceId
        "UGVybWFuZW50VXNlcklk"       # PermanentUserId
    ]
    
    success_count = 0
    
    for file_name_encoded in id_files_encoded:
        try:
            # Decode the filename
            file_name = base64.b64decode(file_name_encoded).decode('utf-8')
            file_path = jetbrains_dir / file_name
            
            info(f"Processing JetBrains ID file: {file_name}")
            
            if update_id_file(file_path):
                if lock_file(file_path):
                    success_count += 1
                else:
                    warning(f"Updated but failed to lock file: {file_path}")
            else:
                error(f"Failed to update file: {file_path}")
                
        except Exception as e:
            error(f"Error processing JetBrains file {file_name_encoded}: {e}")
    
    if success_count > 0:
        success(f"JetBrains ID files have been updated and locked successfully! ({success_count} files)")
        return True
    else:
        error("Failed to update any JetBrains ID files")
        return False

def update_vscode_files(vscode_path: Path, vscode_keys: List[str]) -> bool:
    """
    Update VS Code storage.json file with new telemetry IDs.
    
    Args:
        vscode_path: Path to VS Code storage directory
        vscode_keys: List of base64 encoded keys to update
        
    Returns:
        True if successful, False otherwise
    """
    storage_json_path = vscode_path / "storage.json"
    
    # Handle both storage.json files and direct ID files
    if storage_json_path.exists():
        info(f"Updating VS Code storage: {storage_json_path}")
        
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
                    key = base64.b64decode(key_encoded).decode('utf-8')
                    
                    # Show old value if it exists
                    if key in data:
                        info(f"Old value for {key}: {data[key]}")
                    
                    # Generate and update new value
                    if key_encoded == "dGVsZW1ldHJ5LmRldkRldmljZUlk":  # telemetry.devDeviceId
                        new_value = generate_device_id()
                    else:
                        # Some fields are SHA-256 hashes
                        new_value = generate_sha256_hash()
                    
                    info(f"New value for {key}: {new_value}")
                    data[key] = new_value
                    
                except Exception as e:
                    error(f"Error processing key {key_encoded}: {e}")
                    continue
            
            # Write back to file
            with open(storage_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            success("Successfully wrote new UUIDs to storage.json")
            return True
            
        except Exception as e:
            error(f"Failed to update VS Code storage.json: {e}")
            return False
    
    # Handle direct ID files (if vscode_path is a file)
    elif vscode_path.exists() and vscode_path.is_file():
        return update_id_file(vscode_path) and lock_file(vscode_path)
    
    return True

def modify_vscode_ids() -> bool:
    """
    Modify VS Code variants telemetry IDs.
    
    Returns:
        True if successful, False otherwise
    """
    info("Starting VS Code variants telemetry ID modification")
    
    # Base64 encoded machine ID
    machine_id_encoded = "bWFjaGluZUlk"  # machineId
    
    vscode_dirs = get_vscode_files(machine_id_encoded)
    if not vscode_dirs:
        warning("No VS Code variants found")
        return False
    
    info(f"Found {len(vscode_dirs)} VS Code storage directories")
    
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
        count_query = base64.b64decode(count_query_encoded).decode('utf-8')
        delete_query = base64.b64decode(delete_query_encoded).decode('utf-8')
    except Exception as e:
        error(f"Failed to decode database queries: {e}")
        return False
    
    success_count = 0
    
    for vscode_dir in vscode_dirs:
        info(f"Processing VS Code directory: {vscode_dir}")
        
        try:
            # Update storage files
            if update_vscode_files(vscode_dir, vscode_keys):
                success_count += 1
            
            # Clean databases
            clean_vscode_database(vscode_dir, count_query, delete_query)
            
        except Exception as e:
            error(f"Error processing VS Code directory {vscode_dir}: {e}")
    
    if success_count > 0:
        success(f"All found VS Code variants' ID files have been updated and databases cleaned successfully! ({success_count} directories)")
        return True
    else:
        error("Failed to update any VS Code directories")
        return False

def modify_telemetry_ids() -> bool:
    """
    Modify telemetry IDs across all supported IDEs.
    
    Returns:
        True if any IDE was successfully processed, False otherwise
    """
    info("Starting multi-IDE telemetry ID modification")
    
    programs_found = False
    overall_success = False
    
    # Try to find and update JetBrains
    try:
        if modify_jetbrains_ids():
            programs_found = True
            overall_success = True
    except Exception as e:
        error(f"Error processing JetBrains: {e}")
    
    # Try to find and update VS Code variants
    try:
        if modify_vscode_ids():
            programs_found = True
            overall_success = True
    except Exception as e:
        error(f"Error processing VS Code variants: {e}")
    
    if not programs_found:
        error("No JetBrains or VS Code installations found")
        return False
    
    if overall_success:
        success("Multi-IDE telemetry ID modification completed successfully!")
        info("You may need to restart your IDEs for changes to take effect")
    else:
        warning("Some IDEs were found but modification failed")
    
    return overall_success

# Legacy function for backward compatibility
def modify_telemetry_ids_legacy() -> bool:
    """
    Legacy VS Code telemetry ID modifier (for backward compatibility)
    
    Returns:
        True if successful, False otherwise
    """
    from .utils import get_vscode_paths, backup_file
    
    info("Starting VS Code telemetry ID modification (legacy mode)")
    
    # Get VS Code paths
    paths = get_vscode_paths()
    storage_json = paths["storage_json"]
    
    if not storage_json.exists():
        warning(f"VS Code storage.json not found at: {storage_json}")
        return False
    
    info(f"Found storage.json at: {storage_json}")
    
    # Create backup
    backup_path = backup_file(storage_json)
    
    # Generate new IDs
    info("Generating new telemetry IDs...")
    machine_id = generate_machine_id()
    device_id = generate_device_id()
    
    # Read the current file
    try:
        with open(storage_json, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Update the values
        content["telemetry.machineId"] = machine_id
        content["telemetry.devDeviceId"] = device_id
        
        # Write the updated content back to the file
        with open(storage_json, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        success("Successfully updated telemetry IDs")
        info(f"New machineId: {machine_id}")
        info(f"New devDeviceId: {device_id}")
        info("You may need to restart VS Code for changes to take effect")
        
        return True
        
    except json.JSONDecodeError:
        error("The storage file is not valid JSON")
        return False
    except Exception as e:
        error(f"Unexpected error: {e}")
        return False
