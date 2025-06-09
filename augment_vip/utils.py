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

# IDE Configuration
IDE_CONFIGS = {
    "vscode": {
        "name": "Visual Studio Code",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "Code" / "User" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "Code" / "User",
        ],
        "linux_paths": [
            Path.home() / ".config" / "Code" / "User",
        ],
        "db_files": ["globalStorage/state.vscdb"],
        "config_files": ["globalStorage/storage.json"],
        "supported_operations": ["clean", "modify_ids"]
    },
    "vscode-insiders": {
        "name": "Visual Studio Code Insiders",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "Code - Insiders" / "User" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "Code - Insiders" / "User",
        ],
        "linux_paths": [
            Path.home() / ".config" / "Code - Insiders" / "User",
        ],
        "db_files": ["globalStorage/state.vscdb"],
        "config_files": ["globalStorage/storage.json"],
        "supported_operations": ["clean", "modify_ids"]
    },
    "cursor": {
        "name": "Cursor",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "Cursor" / "User",
        ],
        "linux_paths": [
            Path.home() / ".config" / "Cursor" / "User",
        ],
        "db_files": ["globalStorage/state.vscdb"],
        "config_files": ["globalStorage/storage.json"],
        "supported_operations": ["clean", "modify_ids"]
    },
    "codium": {
        "name": "VSCodium",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "VSCodium" / "User" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "VSCodium" / "User",
        ],
        "linux_paths": [
            Path.home() / ".config" / "VSCodium" / "User",
        ],
        "db_files": ["globalStorage/state.vscdb"],
        "config_files": ["globalStorage/storage.json"],
        "supported_operations": ["clean", "modify_ids"]
    },
    "intellij": {
        "name": "IntelliJ IDEA",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "IntelliJIdea2024.3" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "IntelliJIdea2024.2" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "IntelliJIdea2024.1" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "JetBrains" / "IntelliJIdea2024.3",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "IntelliJIdea2024.2",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "IntelliJIdea2024.1",
        ],
        "linux_paths": [
            Path.home() / ".config" / "JetBrains" / "IntelliJIdea2024.3",
            Path.home() / ".config" / "JetBrains" / "IntelliJIdea2024.2",
            Path.home() / ".config" / "JetBrains" / "IntelliJIdea2024.1",
        ],
        "db_files": ["options/other.xml", "options/ide.general.xml"],
        "config_files": ["options/other.xml"],
        "supported_operations": ["clean"]
    },
    "pycharm": {
        "name": "PyCharm",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "PyCharm2024.3" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "PyCharm2024.2" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "PyCharm2024.1" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "JetBrains" / "PyCharm2024.3",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "PyCharm2024.2",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "PyCharm2024.1",
        ],
        "linux_paths": [
            Path.home() / ".config" / "JetBrains" / "PyCharm2024.3",
            Path.home() / ".config" / "JetBrains" / "PyCharm2024.2",
            Path.home() / ".config" / "JetBrains" / "PyCharm2024.1",
        ],
        "db_files": ["options/other.xml", "options/ide.general.xml"],
        "config_files": ["options/other.xml"],
        "supported_operations": ["clean"]
    },
    "webstorm": {
        "name": "WebStorm",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "WebStorm2024.3" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "WebStorm2024.2" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "WebStorm2024.1" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "JetBrains" / "WebStorm2024.3",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "WebStorm2024.2",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "WebStorm2024.1",
        ],
        "linux_paths": [
            Path.home() / ".config" / "JetBrains" / "WebStorm2024.3",
            Path.home() / ".config" / "JetBrains" / "WebStorm2024.2",
            Path.home() / ".config" / "JetBrains" / "WebStorm2024.1",
        ],
        "db_files": ["options/other.xml", "options/ide.general.xml"],
        "config_files": ["options/other.xml"],
        "supported_operations": ["clean"]
    },
    "phpstorm": {
        "name": "PhpStorm",
        "windows_paths": [
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "PhpStorm2024.3" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "PhpStorm2024.2" if os.environ.get("APPDATA") else None,
            Path(os.environ.get("APPDATA", "")) / "JetBrains" / "PhpStorm2024.1" if os.environ.get("APPDATA") else None,
        ],
        "macos_paths": [
            Path.home() / "Library" / "Application Support" / "JetBrains" / "PhpStorm2024.3",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "PhpStorm2024.2",
            Path.home() / "Library" / "Application Support" / "JetBrains" / "PhpStorm2024.1",
        ],
        "linux_paths": [
            Path.home() / ".config" / "JetBrains" / "PhpStorm2024.3",
            Path.home() / ".config" / "JetBrains" / "PhpStorm2024.2",
            Path.home() / ".config" / "JetBrains" / "PhpStorm2024.1",
        ],
        "db_files": ["options/other.xml", "options/ide.general.xml"],
        "config_files": ["options/other.xml"],
        "supported_operations": ["clean"]
    }
}

_ENCODED_TERMS = [
    "YXVnbWVudA==", 
    "QXVnbWVudA==",
    "QVVHTUVOQA==",
]

_CONFIG_KEYS = {
    "db_pattern_a": "YXVnbWVudA==",
    "db_pattern_b": "QXVnbWVudA==", 
    "db_pattern_c": "QVVHTUVOQA==",
    "legacy_key_1": "YXVnbWVudHM=",
    "legacy_key_2": "YXVnbWVudGVk",  
}

def _rot13_decode(text: str) -> str:
    """
    Simple ROT13 decoding for additional obfuscation
    
    Args:
        text: Text to decode
        
    Returns:
        Decoded text
    """
    result = ""
    for char in text:
        if 'a' <= char <= 'z':
            result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += char
    return result

def _decode_search_terms() -> List[str]:
    """
    Decode the search terms from base64
    
    Returns:
        List of decoded search terms
    """
    terms = []
    
    for key, encoded_term in _CONFIG_KEYS.items():
        try:
            decoded = base64.b64decode(encoded_term).decode('utf-8')
            terms.extend([
                decoded,
                decoded.lower(),
                decoded.upper(),
                decoded.capitalize()
            ])
        except Exception:
            continue
    
    for encoded_term in _ENCODED_TERMS:
        try:
            decoded = base64.b64decode(encoded_term).decode('utf-8')
            terms.extend([
                decoded,
                decoded.lower(),
                decoded.upper(),
                decoded.capitalize()
            ])
        except Exception:
            continue
    
    base_terms = list(set([t.lower() for t in terms]))
    for base_term in base_terms:
        if len(base_term) > 3:
            terms.extend([
                base_term + "s",         
                base_term + "ed",       
                base_term + "ing",         
                base_term.capitalize() + "VIP",  
                base_term.upper() + "_",  
            ])
    
    return list(dict.fromkeys(terms))

def _check_term_match(text: str, terms: List[str]) -> bool:
    """
    Check if any of the terms match in the given text
    
    Args:
        text: Text to search in
        terms: List of terms to search for
        
    Returns:
        True if any term is found, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    for term in terms:
        if term.lower() in text_lower:
            return True
    return False

def get_search_terms() -> List[str]:
    """
    Get the decoded search terms for cleaning operations
    
    Returns:
        List of search terms to look for
    """
    return _decode_search_terms()

def detect_installed_ides() -> List[Tuple[str, str, Path]]:
    """
    Detect installed IDEs on the system
    
    Returns:
        List of tuples (ide_key, ide_name, base_path)
    """
    system = platform.system()
    installed_ides = []
    
    for ide_key, config in IDE_CONFIGS.items():
        paths_key = f"{system.lower()}_paths"
        if system == "Darwin":
            paths_key = "macos_paths"
        
        if paths_key in config:
            for path in config[paths_key]:
                if path and path.exists():
                    installed_ides.append((ide_key, config["name"], path))
                    break 
    
    return installed_ides

def select_ide_interactive() -> Optional[Tuple[str, str, Path]]:
    """
    Interactive IDE selection from detected IDEs
    
    Returns:
        Tuple of (ide_key, ide_name, base_path) or None if cancelled
    """
    installed_ides = detect_installed_ides()
    
    if not installed_ides:
        error("No supported IDEs found on your system")
        info("Supported IDEs:")
        for ide_key, config in IDE_CONFIGS.items():
            info(f"  - {config['name']}")
        return None
    
    print("\n" + "="*50)
    print("AUGMENT VIP - IDE SELECTOR")
    print("="*50)
    print("Detected IDEs:")
    
    for i, (ide_key, ide_name, base_path) in enumerate(installed_ides, 1):
        operations = ", ".join(IDE_CONFIGS[ide_key]["supported_operations"])
        print(f"{i}. {ide_name}")
        print(f"   Path: {base_path}")
        print(f"   Operations: {operations}")
        print()
    
    print("0. Cancel")
    print("-" * 50)
    
    while True:
        try:
            choice = input("Select an IDE (enter number): ").strip()
            
            if choice == "0":
                info("Operation cancelled")
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(installed_ides):
                selected = installed_ides[choice_num - 1]
                success(f"Selected: {selected[1]}")
                return selected
            else:
                error(f"Please enter a number between 0 and {len(installed_ides)}")
                
        except ValueError:
            error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n")
            info("Operation cancelled")
            return None

def get_ide_paths(ide_key: str, base_path: Path) -> Dict[str, Path]:
    """
    Get IDE paths based on the IDE key and base path
    
    Args:
        ide_key: IDE identifier key
        base_path: Base directory path for the IDE
        
    Returns:
        Dict with paths to IDE directories and files
    """
    config = IDE_CONFIGS.get(ide_key)
    if not config:
        error(f"Unknown IDE: {ide_key}")
        sys.exit(1)
    
    paths = {"base_dir": base_path}
    
    for db_file in config["db_files"]:
        db_path = base_path / db_file
        if db_path.exists():
            if "state.vscdb" in db_file:
                paths["state_db"] = db_path
            elif "other.xml" in db_file:
                paths["config_xml"] = db_path
            elif "ide.general.xml" in db_file:
                paths["ide_general_xml"] = db_path
    
    for config_file in config["config_files"]:
        config_path = base_path / config_file
        if config_path.exists():
            if "storage.json" in config_file:
                paths["storage_json"] = config_path
            elif "other.xml" in config_file:
                paths["config_xml"] = config_path
    
    return paths

def get_vscode_paths() -> Dict[str, Path]:
    """
    Get VS Code paths based on the operating system (legacy function for compatibility)
    
    Returns:
        Dict with paths to VS Code directories and files
    """
    return get_ide_paths("vscode", get_ide_base_path("vscode"))

def get_ide_base_path(ide_key: str) -> Path:
    """
    Get the base path for a specific IDE
    
    Args:
        ide_key: IDE identifier key
        
    Returns:
        Base path for the IDE
    """
    system = platform.system()
    config = IDE_CONFIGS.get(ide_key)
    
    if not config:
        error(f"Unknown IDE: {ide_key}")
        sys.exit(1)
    
    paths_key = f"{system.lower()}_paths"
    if system == "Darwin":
        paths_key = "macos_paths"
    
    if paths_key not in config:
        error(f"IDE {ide_key} not supported on {system}")
        sys.exit(1)
    
    for path in config[paths_key]:
        if path and path.exists():
            return path
    
    error(f"IDE {ide_key} not found on your system")
    sys.exit(1)

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

def is_operation_supported(ide_key: str, operation: str) -> bool:
    """
    Check if an operation is supported for a specific IDE
    
    Args:
        ide_key: IDE identifier key
        operation: Operation name (clean, modify_ids, etc.)
        
    Returns:
        True if operation is supported, False otherwise
    """
    config = IDE_CONFIGS.get(ide_key)
    if not config:
        return False
    
    return operation in config.get("supported_operations", [])
