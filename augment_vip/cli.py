"""
Command-line interface for Augment VIP
"""

import os
import sys
import click
from pathlib import Path

from . import __version__
from .utils import (
    info, success, error, warning, 
    select_ide_interactive, detect_installed_ides, 
    get_ide_paths, is_operation_supported, IDE_CONFIGS
)
from .db_cleaner import clean_ide_db
from .id_modifier import modify_ide_telemetry_ids

@click.group()
@click.version_option(version=__version__)
def cli():
    """Augment VIP - Tools for managing IDE settings across multiple editors"""
    pass

@cli.command()
@click.option('--ide', type=str, help='IDE to clean (e.g., vscode, cursor, intellij)')
@click.option('--auto', is_flag=True, help='Auto-detect and clean all supported IDEs')
def clean(ide, auto):
    """Clean IDE databases by removing target entries"""
    if auto:
        # Auto-detect and clean all IDEs
        installed_ides = detect_installed_ides()
        if not installed_ides:
            error("No supported IDEs found on your system")
            sys.exit(1)
        
        success_count = 0
        for ide_key, ide_name, base_path in installed_ides:
            if is_operation_supported(ide_key, "clean"):
                info(f"Cleaning {ide_name}...")
                if clean_ide_db(ide_key, base_path):
                    success(f"Successfully cleaned {ide_name}")
                    success_count += 1
                else:
                    error(f"Failed to clean {ide_name}")
            else:
                warning(f"Clean operation not supported for {ide_name}")
        
        if success_count > 0:
            success(f"Successfully cleaned {success_count} IDE(s)")
        else:
            error("No IDEs were cleaned successfully")
            sys.exit(1)
    
    elif ide:
        # Clean specific IDE
        if ide not in IDE_CONFIGS:
            error(f"Unknown IDE: {ide}")
            error("Supported IDEs:")
            for ide_key, config in IDE_CONFIGS.items():
                error(f"  - {ide_key}: {config['name']}")
            sys.exit(1)
        
        if not is_operation_supported(ide, "clean"):
            error(f"Clean operation not supported for {IDE_CONFIGS[ide]['name']}")
            sys.exit(1)
        
        try:
            from .utils import get_ide_base_path
            base_path = get_ide_base_path(ide)
            if clean_ide_db(ide, base_path):
                success(f"Successfully cleaned {IDE_CONFIGS[ide]['name']}")
            else:
                error(f"Failed to clean {IDE_CONFIGS[ide]['name']}")
                sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            error(f"Error cleaning {IDE_CONFIGS[ide]['name']}: {e}")
            sys.exit(1)
    
    else:
        # Interactive selection
        selected = select_ide_interactive()
        if not selected:
            sys.exit(1)
        
        ide_key, ide_name, base_path = selected
        
        if not is_operation_supported(ide_key, "clean"):
            error(f"Clean operation not supported for {ide_name}")
            sys.exit(1)
        
        if clean_ide_db(ide_key, base_path):
            success(f"Successfully cleaned {ide_name}")
        else:
            error(f"Failed to clean {ide_name}")
            sys.exit(1)

@cli.command()
@click.option('--ide', type=str, help='IDE to modify (e.g., vscode, cursor)')
@click.option('--auto', is_flag=True, help='Auto-detect and modify all supported IDEs')
def modify_ids(ide, auto):
    """Modify IDE telemetry IDs (VS Code-based editors only)"""
    if auto:
        # Auto-detect and modify all IDEs
        installed_ides = detect_installed_ides()
        if not installed_ides:
            error("No supported IDEs found on your system")
            sys.exit(1)
        
        success_count = 0
        for ide_key, ide_name, base_path in installed_ides:
            if is_operation_supported(ide_key, "modify_ids"):
                info(f"Modifying telemetry IDs for {ide_name}...")
                if modify_ide_telemetry_ids(ide_key, base_path):
                    success(f"Successfully modified telemetry IDs for {ide_name}")
                    success_count += 1
                else:
                    error(f"Failed to modify telemetry IDs for {ide_name}")
            else:
                warning(f"Telemetry ID modification not supported for {ide_name}")
        
        if success_count > 0:
            success(f"Successfully modified telemetry IDs for {success_count} IDE(s)")
        else:
            error("No IDE telemetry IDs were modified successfully")
            sys.exit(1)
    
    elif ide:
        # Modify specific IDE
        if ide not in IDE_CONFIGS:
            error(f"Unknown IDE: {ide}")
            error("Supported IDEs:")
            for ide_key, config in IDE_CONFIGS.items():
                error(f"  - {ide_key}: {config['name']}")
            sys.exit(1)
        
        if not is_operation_supported(ide, "modify_ids"):
            error(f"Telemetry ID modification not supported for {IDE_CONFIGS[ide]['name']}")
            error("This operation is only supported for VS Code-based editors")
            sys.exit(1)
        
        try:
            from .utils import get_ide_base_path
            base_path = get_ide_base_path(ide)
            if modify_ide_telemetry_ids(ide, base_path):
                success(f"Successfully modified telemetry IDs for {IDE_CONFIGS[ide]['name']}")
            else:
                error(f"Failed to modify telemetry IDs for {IDE_CONFIGS[ide]['name']}")
                sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            error(f"Error modifying telemetry IDs for {IDE_CONFIGS[ide]['name']}: {e}")
            sys.exit(1)
    
    else:
        # Interactive selection
        selected = select_ide_interactive()
        if not selected:
            sys.exit(1)
        
        ide_key, ide_name, base_path = selected
        
        if not is_operation_supported(ide_key, "modify_ids"):
            error(f"Telemetry ID modification not supported for {ide_name}")
            error("This operation is only supported for VS Code-based editors")
            sys.exit(1)
        
        if modify_ide_telemetry_ids(ide_key, base_path):
            success(f"Successfully modified telemetry IDs for {ide_name}")
        else:
            error(f"Failed to modify telemetry IDs for {ide_name}")
            sys.exit(1)

@cli.command()
@click.option('--ide', type=str, help='IDE to process (e.g., vscode, cursor, intellij)')
@click.option('--auto', is_flag=True, help='Auto-detect and process all supported IDEs')
def all(ide, auto):
    """Run all supported tools for the selected IDE(s)"""
    if auto:
        # Auto-detect and process all IDEs
        installed_ides = detect_installed_ides()
        if not installed_ides:
            error("No supported IDEs found on your system")
            sys.exit(1)
        
        success_count = 0
        for ide_key, ide_name, base_path in installed_ides:
            info(f"Processing {ide_name}...")
            
            clean_result = False
            modify_result = False
            
            if is_operation_supported(ide_key, "clean"):
                info(f"Cleaning {ide_name}...")
                clean_result = clean_ide_db(ide_key, base_path)
                if clean_result:
                    success(f"Successfully cleaned {ide_name}")
                else:
                    error(f"Failed to clean {ide_name}")
            
            if is_operation_supported(ide_key, "modify_ids"):
                info(f"Modifying telemetry IDs for {ide_name}...")
                modify_result = modify_ide_telemetry_ids(ide_key, base_path)
                if modify_result:
                    success(f"Successfully modified telemetry IDs for {ide_name}")
                else:
                    error(f"Failed to modify telemetry IDs for {ide_name}")
            
            if clean_result or modify_result:
                success_count += 1
        
        if success_count > 0:
            success(f"Successfully processed {success_count} IDE(s)")
        else:
            error("No IDEs were processed successfully")
            sys.exit(1)
    
    elif ide:
        # Process specific IDE
        if ide not in IDE_CONFIGS:
            error(f"Unknown IDE: {ide}")
            error("Supported IDEs:")
            for ide_key, config in IDE_CONFIGS.items():
                error(f"  - {ide_key}: {config['name']}")
            sys.exit(1)
        
        try:
            from .utils import get_ide_base_path
            base_path = get_ide_base_path(ide)
            
            clean_result = False
            modify_result = False
            
            if is_operation_supported(ide, "clean"):
                info(f"Cleaning {IDE_CONFIGS[ide]['name']}...")
                clean_result = clean_ide_db(ide, base_path)
            
            if is_operation_supported(ide, "modify_ids"):
                info(f"Modifying telemetry IDs for {IDE_CONFIGS[ide]['name']}...")
                modify_result = modify_ide_telemetry_ids(ide, base_path)
            
            if clean_result and modify_result:
                success(f"All operations completed successfully for {IDE_CONFIGS[ide]['name']}")
            elif clean_result or modify_result:
                success(f"Some operations completed successfully for {IDE_CONFIGS[ide]['name']}")
            else:
                error(f"All operations failed for {IDE_CONFIGS[ide]['name']}")
                sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            error(f"Error processing {IDE_CONFIGS[ide]['name']}: {e}")
            sys.exit(1)
    
    else:
        # Interactive selection
        selected = select_ide_interactive()
        if not selected:
            sys.exit(1)
        
        ide_key, ide_name, base_path = selected
        
        clean_result = False
        modify_result = False
        
        if is_operation_supported(ide_key, "clean"):
            info(f"Cleaning {ide_name}...")
            clean_result = clean_ide_db(ide_key, base_path)
        
        if is_operation_supported(ide_key, "modify_ids"):
            info(f"Modifying telemetry IDs for {ide_name}...")
            modify_result = modify_ide_telemetry_ids(ide_key, base_path)
        
        if clean_result and modify_result:
            success(f"All operations completed successfully for {ide_name}")
        elif clean_result or modify_result:
            success(f"Some operations completed successfully for {ide_name}")
        else:
            error(f"All operations failed for {ide_name}")
            sys.exit(1)

@cli.command()
def list_ides():
    """List all supported IDEs and their installation status"""
    info("Scanning for installed IDEs...")
    installed_ides = detect_installed_ides()
    
    print("\n" + "="*60)
    print("SUPPORTED IDEs")
    print("="*60)
    
    for ide_key, config in IDE_CONFIGS.items():
        status = "❌ Not Found"
        path = "N/A"
        operations = ", ".join(config["supported_operations"])
        
        # Check if this IDE is installed
        for inst_key, inst_name, inst_path in installed_ides:
            if inst_key == ide_key:
                status = "✅ Installed"
                path = str(inst_path)
                break
        
        print(f"\n{config['name']} ({ide_key})")
        print(f"  Status: {status}")
        print(f"  Path: {path}")
        print(f"  Operations: {operations}")
    
    if installed_ides:
        print(f"\n{len(installed_ides)} IDE(s) found on your system")
    else:
        print("\nNo supported IDEs found on your system")

@cli.command()
def install():
    """Install Augment VIP"""
    info("Installing Augment VIP...")
    
    # This is a placeholder for any installation steps
    # In Python, most of the installation is handled by pip/setup.py
    
    success("Augment VIP installed successfully")
    info("You can now use the following commands:")
    info("  - augment-vip list-ides: List all supported IDEs")
    info("  - augment-vip clean: Clean IDE databases (interactive)")
    info("  - augment-vip clean --auto: Clean all detected IDEs")
    info("  - augment-vip clean --ide vscode: Clean specific IDE")
    info("  - augment-vip modify-ids: Modify telemetry IDs (VS Code-based editors)")
    info("  - augment-vip all: Run all tools (interactive)")
    info("  - augment-vip all --auto: Run all tools on all detected IDEs")

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except Exception as e:
        error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
