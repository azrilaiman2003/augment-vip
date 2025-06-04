"""
Command-line interface for Augment VIP
"""

import os
import sys
import click
from pathlib import Path

from . import __version__
from .utils import info, success, error, warning
from .db_cleaner import clean_vscode_db
from .id_modifier import modify_telemetry_ids, modify_jetbrains_ids, modify_vscode_ids, modify_telemetry_ids_legacy

@click.group()
@click.version_option(version=__version__)
def cli():
    """Augment VIP - Tools for managing IDE settings across VS Code variants, JetBrains IDEs, and more"""
    pass

@cli.command()
def clean():
    """Clean VS Code databases by removing Augment-related entries"""
    if clean_vscode_db():
        success("Database cleaning completed successfully")
    else:
        error("Database cleaning failed")
        sys.exit(1)

@cli.command()
@click.option('--jetbrains', is_flag=True, help='Only modify JetBrains IDEs')
@click.option('--vscode', is_flag=True, help='Only modify VS Code variants')
@click.option('--legacy', is_flag=True, help='Use legacy VS Code modification (single installation)')
def modify_ids(jetbrains, vscode, legacy):
    """Modify telemetry IDs across supported IDEs"""
    if legacy:
        info("Using legacy VS Code modification mode")
        if modify_telemetry_ids_legacy():
            success("Legacy telemetry ID modification completed successfully")
        else:
            error("Legacy telemetry ID modification failed")
            sys.exit(1)
    elif jetbrains and not vscode:
        info("Modifying JetBrains IDEs only")
        if modify_jetbrains_ids():
            success("JetBrains telemetry ID modification completed successfully")
        else:
            error("JetBrains telemetry ID modification failed")
            sys.exit(1)
    elif vscode and not jetbrains:
        info("Modifying VS Code variants only")
        if modify_vscode_ids():
            success("VS Code telemetry ID modification completed successfully")
        else:
            error("VS Code telemetry ID modification failed")
            sys.exit(1)
    else:
        # Default: modify all supported IDEs
        if modify_telemetry_ids():
            success("Multi-IDE telemetry ID modification completed successfully")
        else:
            error("Telemetry ID modification failed")
            sys.exit(1)

@cli.command()
def jetbrains():
    """Modify JetBrains IDE telemetry IDs only"""
    if modify_jetbrains_ids():
        success("JetBrains telemetry ID modification completed successfully")
    else:
        error("JetBrains telemetry ID modification failed")
        sys.exit(1)

@cli.command()
def vscode():
    """Modify VS Code variant telemetry IDs only"""
    if modify_vscode_ids():
        success("VS Code telemetry ID modification completed successfully")
    else:
        error("VS Code telemetry ID modification failed")
        sys.exit(1)

@cli.command()
@click.option('--skip-clean', is_flag=True, help='Skip database cleaning')
@click.option('--jetbrains-only', is_flag=True, help='Only process JetBrains IDEs')
@click.option('--vscode-only', is_flag=True, help='Only process VS Code variants')
def all(skip_clean, jetbrains_only, vscode_only):
    """Run all tools (clean and modify IDs) across all supported IDEs"""
    info("Running all tools...")
    
    clean_result = True
    if not skip_clean and not jetbrains_only:
        info("Cleaning VS Code databases...")
        clean_result = clean_vscode_db()
    
    # Modify IDs based on options
    if jetbrains_only:
        modify_result = modify_jetbrains_ids()
    elif vscode_only:
        modify_result = modify_vscode_ids()
    else:
        modify_result = modify_telemetry_ids()
    
    if clean_result and modify_result:
        success("All operations completed successfully")
    else:
        error("Some operations failed")
        sys.exit(1)

@cli.command()
def status():
    """Show status of detected IDEs and configuration directories"""
    from .utils import get_jetbrains_config_dir, get_vscode_files
    import base64
    
    info("Scanning for supported IDEs...")
    
    # Check JetBrains
    jetbrains_dir = get_jetbrains_config_dir()
    if jetbrains_dir:
        success(f"JetBrains config directory found: {jetbrains_dir}")
        
        # Check for ID files
        id_files_encoded = ["UGVybWFuZW50RGV2aWNlSWQ=", "UGVybWFuZW50VXNlcklk"]
        for file_encoded in id_files_encoded:
            file_name = base64.b64decode(file_encoded).decode('utf-8')
            file_path = jetbrains_dir / file_name
            if file_path.exists():
                info(f"  Found ID file: {file_name}")
            else:
                warning(f"  ID file not found: {file_name}")
    else:
        warning("No JetBrains installation found")
    
    # Check VS Code variants
    machine_id_encoded = "bWFjaGluZUlk"  # machineId
    vscode_dirs = get_vscode_files(machine_id_encoded)
    if vscode_dirs:
        success(f"Found {len(vscode_dirs)} VS Code storage directories:")
        for vscode_dir in vscode_dirs:
            info(f"  {vscode_dir}")
            storage_json = vscode_dir / "storage.json"
            if storage_json.exists():
                info(f"    storage.json: Found")
            else:
                warning(f"    storage.json: Not found")
    else:
        warning("No VS Code variants found")

@cli.command()
def install():
    """Install Augment VIP"""
    info("Installing Augment VIP...")
    
    # This is a placeholder for any installation steps
    # In Python, most of the installation is handled by pip/setup.py
    
    success("Augment VIP installed successfully")
    info("You can now use the following commands:")
    info("  - augment-vip status: Show detected IDEs")
    info("  - augment-vip clean: Clean VS Code databases")
    info("  - augment-vip modify-ids: Modify telemetry IDs (all IDEs)")
    info("  - augment-vip jetbrains: Modify JetBrains IDs only")
    info("  - augment-vip vscode: Modify VS Code IDs only")
    info("  - augment-vip all: Run all tools")

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except Exception as e:
        error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
