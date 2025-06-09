"""
Command-line interface for Augment VIP
"""

import os
import sys
import time
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

# Modern CLI styling
LOGO = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   █████╗ ██╗   ██╗ ██████╗ ███╗   ███╗███████╗███╗   ██╗████████╗           ║
║  ██╔══██╗██║   ██║██╔════╝ ████╗ ████║██╔════╝████╗  ██║╚══██╔══╝           ║
║  ███████║██║   ██║██║  ███╗██╔████╔██║█████╗  ██╔██╗ ██║   ██║              ║
║  ██╔══██║██║   ██║██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║              ║
║  ██║  ██║╚██████╔╝╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║   ██║              ║
║  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝              ║
║                                                                              ║
║                        ██╗   ██╗██╗██████╗                                  ║
║                        ██║   ██║██║██╔══██╗                                 ║
║                        ██║   ██║██║██████╔╝                                 ║
║                        ╚██╗ ██╔╝██║██╔═══╝                                  ║
║                         ╚████╔╝ ██║██║                                      ║
║                          ╚═══╝  ╚═╝╚═╝                                      ║
║                                                                              ║
║               🚀 Multi-IDE Management & Optimization Tool 🚀                ║
║                            Version """ + __version__ + """                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

def print_logo():
    """Print the modern ASCII logo"""
    click.echo(click.style(LOGO, fg='cyan', bold=True))

def print_section_header(title: str, icon: str = "🔧"):
    """Print a modern section header"""
    separator = "═" * 80
    click.echo()
    click.echo(click.style(f"╔{separator}╗", fg='blue', bold=True))
    click.echo(click.style(f"║{icon}  {title.center(76)}  ║", fg='blue', bold=True))
    click.echo(click.style(f"╚{separator}╝", fg='blue', bold=True))
    click.echo()

def print_operation_result(operation: str, ide_name: str, success_flag: bool):
    """Print operation result with modern styling"""
    if success_flag:
        icon = "✅"
        color = "green"
        status = "SUCCESS"
    else:
        icon = "❌"
        color = "red"
        status = "FAILED"
    
    click.echo(click.style(f"  {icon} {operation} │ {ide_name} │ {status}", fg=color, bold=True))

def show_progress(message: str, duration: float = 1.0):
    """Show a progress indicator"""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for char in chars:
            if time.time() >= end_time:
                break
            click.echo(f"\r{click.style(char, fg='cyan')} {message}", nl=False)
            time.sleep(0.1)
    
    click.echo(f"\r{click.style('✓', fg='green')} {message} - Complete!")

def print_ide_summary(installed_ides):
    """Print a summary of detected IDEs"""
    if not installed_ides:
        click.echo(click.style("  ❌ No supported IDEs found on your system", fg='red', bold=True))
        return
    
    click.echo(click.style(f"  📊 Found {len(installed_ides)} supported IDE(s):", fg='green', bold=True))
    click.echo()
    
    for ide_key, ide_name, base_path in installed_ides:
        operations = IDE_CONFIGS[ide_key]["supported_operations"]
        op_icons = []
        for op in operations:
            if op == "clean":
                op_icons.append("🧹 Clean")
            elif op == "modify_ids":
                op_icons.append("🔄 Modify IDs")
        
        click.echo(click.style(f"    🎯 {ide_name}", fg='cyan', bold=True))
        click.echo(click.style(f"      📁 {base_path}", fg='white', dim=True))
        click.echo(click.style(f"      ⚙️  {' | '.join(op_icons)}", fg='yellow'))
        click.echo()

@click.group()
@click.version_option(version=__version__)
def cli():
    """🚀 Augment VIP - Advanced Multi-IDE Management Tool"""
    pass

@cli.command()
@click.option('--ide', type=str, help='🎯 Target specific IDE (e.g., vscode, cursor, intellij)')
@click.option('--auto', is_flag=True, help='🤖 Auto-detect and clean all supported IDEs')
def clean(ide, auto):
    """🧹 Clean IDE databases by removing target entries"""
    print_logo()
    print_section_header("DATABASE CLEANING OPERATION", "🧹")
    
    if auto:
        click.echo(click.style("🤖 Auto-detection mode enabled", fg='blue', bold=True))
        show_progress("Scanning for installed IDEs", 1.5)
        
        installed_ides = detect_installed_ides()
        if not installed_ides:
            click.echo(click.style("❌ No supported IDEs found on your system", fg='red', bold=True))
            sys.exit(1)
        
        print_ide_summary(installed_ides)
        
        click.echo(click.style("🚀 Starting batch cleaning operation...", fg='green', bold=True))
        click.echo()
        
        success_count = 0
        for ide_key, ide_name, base_path in installed_ides:
            if is_operation_supported(ide_key, "clean"):
                show_progress(f"Cleaning {ide_name}", 0.8)
                result = clean_ide_db(ide_key, base_path)
                print_operation_result("CLEAN", ide_name, result)
                if result:
                    success_count += 1
            else:
                click.echo(click.style(f"  ⚠️  CLEAN │ {ide_name} │ NOT SUPPORTED", fg='yellow'))
        
        click.echo()
        if success_count > 0:
            click.echo(click.style(f"🎉 Successfully cleaned {success_count} IDE(s)!", fg='green', bold=True))
        else:
            click.echo(click.style("❌ No IDEs were cleaned successfully", fg='red', bold=True))
            sys.exit(1)
    
    elif ide:
        click.echo(click.style(f"🎯 Target IDE: {ide}", fg='blue', bold=True))
        
        if ide not in IDE_CONFIGS:
            click.echo(click.style(f"❌ Unknown IDE: {ide}", fg='red', bold=True))
            click.echo(click.style("📋 Supported IDEs:", fg='yellow', bold=True))
            for ide_key, config in IDE_CONFIGS.items():
                click.echo(click.style(f"  • {ide_key}: {config['name']}", fg='white'))
            sys.exit(1)
        
        if not is_operation_supported(ide, "clean"):
            click.echo(click.style(f"❌ Clean operation not supported for {IDE_CONFIGS[ide]['name']}", fg='red', bold=True))
            sys.exit(1)
        
        try:
            from .utils import get_ide_base_path
            base_path = get_ide_base_path(ide)
            
            show_progress(f"Cleaning {IDE_CONFIGS[ide]['name']}", 1.2)
            result = clean_ide_db(ide, base_path)
            print_operation_result("CLEAN", IDE_CONFIGS[ide]['name'], result)
            
            if result:
                click.echo(click.style(f"🎉 Successfully cleaned {IDE_CONFIGS[ide]['name']}!", fg='green', bold=True))
            else:
                click.echo(click.style(f"❌ Failed to clean {IDE_CONFIGS[ide]['name']}", fg='red', bold=True))
                sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            click.echo(click.style(f"💥 Error cleaning {IDE_CONFIGS[ide]['name']}: {e}", fg='red', bold=True))
            sys.exit(1)
    
    else:
        click.echo(click.style("🎮 Interactive mode - Select your target", fg='blue', bold=True))
        selected = select_ide_interactive()
        if not selected:
            sys.exit(1)
        
        ide_key, ide_name, base_path = selected
        
        if ide_key == "__ALL__":
            click.echo(click.style("🚀 Processing all detected IDEs...", fg='green', bold=True))
            click.echo()
            
            installed_ides = detect_installed_ides()
            success_count = 0
            
            for single_ide_key, single_ide_name, single_base_path in installed_ides:
                if is_operation_supported(single_ide_key, "clean"):
                    show_progress(f"Cleaning {single_ide_name}", 0.8)
                    result = clean_ide_db(single_ide_key, single_base_path)
                    print_operation_result("CLEAN", single_ide_name, result)
                    if result:
                        success_count += 1
                else:
                    click.echo(click.style(f"  ⚠️  CLEAN │ {single_ide_name} │ NOT SUPPORTED", fg='yellow'))
            
            click.echo()
            if success_count > 0:
                click.echo(click.style(f"🎉 Successfully cleaned {success_count} IDE(s)!", fg='green', bold=True))
            else:
                click.echo(click.style("❌ No IDEs were cleaned successfully", fg='red', bold=True))
                sys.exit(1)
        else:
            if not is_operation_supported(ide_key, "clean"):
                click.echo(click.style(f"❌ Clean operation not supported for {ide_name}", fg='red', bold=True))
                sys.exit(1)
            
            show_progress(f"Cleaning {ide_name}", 1.2)
            result = clean_ide_db(ide_key, base_path)
            print_operation_result("CLEAN", ide_name, result)
            
            if result:
                click.echo(click.style(f"🎉 Successfully cleaned {ide_name}!", fg='green', bold=True))
            else:
                click.echo(click.style(f"❌ Failed to clean {ide_name}", fg='red', bold=True))
                sys.exit(1)

@cli.command()
@click.option('--ide', type=str, help='🎯 Target specific IDE (e.g., vscode, cursor)')
@click.option('--auto', is_flag=True, help='🤖 Auto-detect and modify all supported IDEs')
def modify_ids(ide, auto):
    """🔄 Modify IDE telemetry IDs (VS Code-based editors only)"""
    print_logo()
    print_section_header("TELEMETRY ID MODIFICATION", "🔄")
    
    if auto:
        click.echo(click.style("🤖 Auto-detection mode enabled", fg='blue', bold=True))
        show_progress("Scanning for installed IDEs", 1.5)
        
        installed_ides = detect_installed_ides()
        if not installed_ides:
            click.echo(click.style("❌ No supported IDEs found on your system", fg='red', bold=True))
            sys.exit(1)
        
        print_ide_summary(installed_ides)
        
        click.echo(click.style("🚀 Starting batch telemetry modification...", fg='green', bold=True))
        click.echo()
        
        success_count = 0
        for ide_key, ide_name, base_path in installed_ides:
            if is_operation_supported(ide_key, "modify_ids"):
                show_progress(f"Modifying telemetry IDs for {ide_name}", 1.0)
                result = modify_ide_telemetry_ids(ide_key, base_path)
                print_operation_result("MODIFY IDS", ide_name, result)
                if result:
                    success_count += 1
            else:
                click.echo(click.style(f"  ⚠️  MODIFY IDS │ {ide_name} │ NOT SUPPORTED", fg='yellow'))
        
        click.echo()
        if success_count > 0:
            click.echo(click.style(f"🎉 Successfully modified telemetry IDs for {success_count} IDE(s)!", fg='green', bold=True))
        else:
            click.echo(click.style("❌ No IDE telemetry IDs were modified successfully", fg='red', bold=True))
            sys.exit(1)
    
    elif ide:
        click.echo(click.style(f"🎯 Target IDE: {ide}", fg='blue', bold=True))
        
        if ide not in IDE_CONFIGS:
            click.echo(click.style(f"❌ Unknown IDE: {ide}", fg='red', bold=True))
            click.echo(click.style("📋 Supported IDEs:", fg='yellow', bold=True))
            for ide_key, config in IDE_CONFIGS.items():
                click.echo(click.style(f"  • {ide_key}: {config['name']}", fg='white'))
            sys.exit(1)
        
        if not is_operation_supported(ide, "modify_ids"):
            click.echo(click.style(f"❌ Telemetry ID modification not supported for {IDE_CONFIGS[ide]['name']}", fg='red', bold=True))
            click.echo(click.style("ℹ️  This operation is only supported for VS Code-based editors", fg='blue'))
            sys.exit(1)
        
        try:
            from .utils import get_ide_base_path
            base_path = get_ide_base_path(ide)
            
            show_progress(f"Modifying telemetry IDs for {IDE_CONFIGS[ide]['name']}", 1.5)
            result = modify_ide_telemetry_ids(ide, base_path)
            print_operation_result("MODIFY IDS", IDE_CONFIGS[ide]['name'], result)
            
            if result:
                click.echo(click.style(f"🎉 Successfully modified telemetry IDs for {IDE_CONFIGS[ide]['name']}!", fg='green', bold=True))
            else:
                click.echo(click.style(f"❌ Failed to modify telemetry IDs for {IDE_CONFIGS[ide]['name']}", fg='red', bold=True))
                sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            click.echo(click.style(f"💥 Error modifying telemetry IDs for {IDE_CONFIGS[ide]['name']}: {e}", fg='red', bold=True))
            sys.exit(1)
    
    else:
        click.echo(click.style("🎮 Interactive mode - Select your target", fg='blue', bold=True))
        selected = select_ide_interactive()
        if not selected:
            sys.exit(1)
        
        ide_key, ide_name, base_path = selected
        
        if ide_key == "__ALL__":
            click.echo(click.style("🚀 Processing all detected IDEs...", fg='green', bold=True))
            click.echo()
            
            installed_ides = detect_installed_ides()
            success_count = 0
            
            for single_ide_key, single_ide_name, single_base_path in installed_ides:
                if is_operation_supported(single_ide_key, "modify_ids"):
                    show_progress(f"Modifying telemetry IDs for {single_ide_name}", 1.0)
                    result = modify_ide_telemetry_ids(single_ide_key, single_base_path)
                    print_operation_result("MODIFY IDS", single_ide_name, result)
                    if result:
                        success_count += 1
                else:
                    click.echo(click.style(f"  ⚠️  MODIFY IDS │ {single_ide_name} │ NOT SUPPORTED", fg='yellow'))
            
            click.echo()
            if success_count > 0:
                click.echo(click.style(f"🎉 Successfully modified telemetry IDs for {success_count} IDE(s)!", fg='green', bold=True))
            else:
                click.echo(click.style("❌ No IDE telemetry IDs were modified successfully", fg='red', bold=True))
                sys.exit(1)
        else:
            if not is_operation_supported(ide_key, "modify_ids"):
                click.echo(click.style(f"❌ Telemetry ID modification not supported for {ide_name}", fg='red', bold=True))
                click.echo(click.style("ℹ️  This operation is only supported for VS Code-based editors", fg='blue'))
                sys.exit(1)
            
            show_progress(f"Modifying telemetry IDs for {ide_name}", 1.5)
            result = modify_ide_telemetry_ids(ide_key, base_path)
            print_operation_result("MODIFY IDS", ide_name, result)
            
            if result:
                click.echo(click.style(f"🎉 Successfully modified telemetry IDs for {ide_name}!", fg='green', bold=True))
            else:
                click.echo(click.style(f"❌ Failed to modify telemetry IDs for {ide_name}", fg='red', bold=True))
                sys.exit(1)

@cli.command()
@click.option('--ide', type=str, help='🎯 Target specific IDE (e.g., vscode, cursor, intellij)')
@click.option('--auto', is_flag=True, help='🤖 Auto-detect and process all supported IDEs')
def all(ide, auto):
    """🚀 Run all available operations on IDEs"""
    print_logo()
    print_section_header("COMPLETE IDE OPTIMIZATION", "🚀")
    
    if auto:
        click.echo(click.style("🤖 Auto-detection mode enabled", fg='blue', bold=True))
        show_progress("Scanning for installed IDEs", 1.5)
        
        installed_ides = detect_installed_ides()
        if not installed_ides:
            click.echo(click.style("❌ No supported IDEs found on your system", fg='red', bold=True))
            sys.exit(1)
        
        print_ide_summary(installed_ides)
        
        click.echo(click.style("🚀 Starting complete optimization process...", fg='green', bold=True))
        click.echo()
        
        success_count = 0
        for ide_key, ide_name, base_path in installed_ides:
            click.echo(click.style(f"🎯 Processing {ide_name}...", fg='cyan', bold=True))
            
            clean_result = False
            modify_result = False
            
            if is_operation_supported(ide_key, "clean"):
                show_progress(f"  🧹 Cleaning {ide_name}", 0.8)
                clean_result = clean_ide_db(ide_key, base_path)
                print_operation_result("CLEAN", ide_name, clean_result)
            
            if is_operation_supported(ide_key, "modify_ids"):
                show_progress(f"  🔄 Modifying telemetry IDs for {ide_name}", 1.0)
                modify_result = modify_ide_telemetry_ids(ide_key, base_path)
                print_operation_result("MODIFY IDS", ide_name, modify_result)
            
            if clean_result or modify_result:
                success_count += 1
            
            click.echo()
        
        if success_count > 0:
            click.echo(click.style(f"🎉 Successfully processed {success_count} IDE(s)!", fg='green', bold=True))
        else:
            click.echo(click.style("❌ No IDEs were processed successfully", fg='red', bold=True))
            sys.exit(1)
    
    elif ide:
        click.echo(click.style(f"🎯 Target IDE: {ide}", fg='blue', bold=True))
        
        if ide not in IDE_CONFIGS:
            click.echo(click.style(f"❌ Unknown IDE: {ide}", fg='red', bold=True))
            click.echo(click.style("📋 Supported IDEs:", fg='yellow', bold=True))
            for ide_key, config in IDE_CONFIGS.items():
                click.echo(click.style(f"  • {ide_key}: {config['name']}", fg='white'))
            sys.exit(1)
        
        try:
            from .utils import get_ide_base_path
            base_path = get_ide_base_path(ide)
            
            click.echo(click.style(f"🚀 Starting complete optimization for {IDE_CONFIGS[ide]['name']}...", fg='green', bold=True))
            click.echo()
            
            clean_result = False
            modify_result = False
            
            if is_operation_supported(ide, "clean"):
                show_progress(f"🧹 Cleaning {IDE_CONFIGS[ide]['name']}", 1.0)
                clean_result = clean_ide_db(ide, base_path)
                print_operation_result("CLEAN", IDE_CONFIGS[ide]['name'], clean_result)
            
            if is_operation_supported(ide, "modify_ids"):
                show_progress(f"🔄 Modifying telemetry IDs for {IDE_CONFIGS[ide]['name']}", 1.2)
                modify_result = modify_ide_telemetry_ids(ide, base_path)
                print_operation_result("MODIFY IDS", IDE_CONFIGS[ide]['name'], modify_result)
            
            click.echo()
            if clean_result and modify_result:
                click.echo(click.style(f"🎉 All operations completed successfully for {IDE_CONFIGS[ide]['name']}!", fg='green', bold=True))
            elif clean_result or modify_result:
                click.echo(click.style(f"⚠️  Some operations completed successfully for {IDE_CONFIGS[ide]['name']}", fg='yellow', bold=True))
            else:
                click.echo(click.style(f"❌ All operations failed for {IDE_CONFIGS[ide]['name']}", fg='red', bold=True))
                sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            click.echo(click.style(f"💥 Error processing {IDE_CONFIGS[ide]['name']}: {e}", fg='red', bold=True))
            sys.exit(1)
    
    else:
        click.echo(click.style("🎮 Interactive mode - Select your target", fg='blue', bold=True))
        selected = select_ide_interactive()
        if not selected:
            sys.exit(1)
        
        ide_key, ide_name, base_path = selected
        
        if ide_key == "__ALL__":
            click.echo(click.style("🚀 Processing all detected IDEs...", fg='green', bold=True))
            click.echo()
            
            installed_ides = detect_installed_ides()
            success_count = 0
            
            for single_ide_key, single_ide_name, single_base_path in installed_ides:
                click.echo(click.style(f"🎯 Processing {single_ide_name}...", fg='cyan', bold=True))
                
                clean_result = False
                modify_result = False
                
                if is_operation_supported(single_ide_key, "clean"):
                    show_progress(f"  🧹 Cleaning {single_ide_name}", 0.8)
                    clean_result = clean_ide_db(single_ide_key, single_base_path)
                    print_operation_result("CLEAN", single_ide_name, clean_result)
                
                if is_operation_supported(single_ide_key, "modify_ids"):
                    show_progress(f"  🔄 Modifying telemetry IDs for {single_ide_name}", 1.0)
                    modify_result = modify_ide_telemetry_ids(single_ide_key, single_base_path)
                    print_operation_result("MODIFY IDS", single_ide_name, modify_result)
                
                if clean_result or modify_result:
                    success_count += 1
                
                click.echo()
            
            if success_count > 0:
                click.echo(click.style(f"🎉 Successfully processed {success_count} IDE(s)!", fg='green', bold=True))
            else:
                click.echo(click.style("❌ No IDEs were processed successfully", fg='red', bold=True))
                sys.exit(1)
        else:
            click.echo(click.style(f"🚀 Starting complete optimization for {ide_name}...", fg='green', bold=True))
            click.echo()
            
            clean_result = False
            modify_result = False
            
            if is_operation_supported(ide_key, "clean"):
                show_progress(f"🧹 Cleaning {ide_name}", 1.0)
                clean_result = clean_ide_db(ide_key, base_path)
                print_operation_result("CLEAN", ide_name, clean_result)
            
            if is_operation_supported(ide_key, "modify_ids"):
                show_progress(f"🔄 Modifying telemetry IDs for {ide_name}", 1.2)
                modify_result = modify_ide_telemetry_ids(ide_key, base_path)
                print_operation_result("MODIFY IDS", ide_name, modify_result)
            
            click.echo()
            if clean_result and modify_result:
                click.echo(click.style(f"🎉 All operations completed successfully for {ide_name}!", fg='green', bold=True))
            elif clean_result or modify_result:
                click.echo(click.style(f"⚠️  Some operations completed successfully for {ide_name}", fg='yellow', bold=True))
            else:
                click.echo(click.style(f"❌ All operations failed for {ide_name}", fg='red', bold=True))
                sys.exit(1)

@cli.command()
def list_ides():
    """📋 List all supported IDEs and their installation status"""
    print_logo()
    print_section_header("IDE DETECTION & STATUS REPORT", "📋")
    
    show_progress("Scanning for installed IDEs", 2.0)
    installed_ides = detect_installed_ides()
    
    click.echo(click.style("╔════════════════════════════════════════════════════════════════════════════╗", fg='blue', bold=True))
    click.echo(click.style("║                            SUPPORTED IDEs                                 ║", fg='blue', bold=True))
    click.echo(click.style("╚════════════════════════════════════════════════════════════════════════════╝", fg='blue', bold=True))
    click.echo()
    
    for ide_key, config in IDE_CONFIGS.items():
        status_icon = "❌"
        status_text = "Not Found"
        status_color = "red"
        path = "N/A"
        
        # Check if this IDE is installed
        for inst_key, inst_name, inst_path in installed_ides:
            if inst_key == ide_key:
                status_icon = "✅"
                status_text = "Installed"
                status_color = "green"
                path = str(inst_path)
                break
        
        operations = config["supported_operations"]
        op_icons = []
        for op in operations:
            if op == "clean":
                op_icons.append("🧹 Clean")
            elif op == "modify_ids":
                op_icons.append("🔄 Modify IDs")
        
        click.echo(click.style(f"🎯 {config['name']} ({ide_key})", fg='cyan', bold=True))
        click.echo(click.style(f"   Status: {status_icon} {status_text}", fg=status_color, bold=True))
        click.echo(click.style(f"   Path: {path}", fg='white', dim=True))
        click.echo(click.style(f"   Operations: {' | '.join(op_icons)}", fg='yellow'))
        click.echo()
    
    if installed_ides:
        click.echo(click.style(f"🎉 {len(installed_ides)} IDE(s) found on your system", fg='green', bold=True))
    else:
        click.echo(click.style("❌ No supported IDEs found on your system", fg='red', bold=True))
    
    click.echo()

@cli.command()
def install():
    """⚙️ Install and setup Augment VIP"""
    print_logo()
    print_section_header("INSTALLATION & SETUP", "⚙️")
    
    show_progress("Setting up Augment VIP", 2.0)
    
    click.echo(click.style("🎉 Augment VIP installed successfully!", fg='green', bold=True))
    click.echo()
    click.echo(click.style("📚 Available Commands:", fg='cyan', bold=True))
    
    commands = [
        ("📋 list-ides", "List all supported IDEs and their status"),
        ("🧹 clean", "Clean IDE databases (interactive or batch)"),
        ("🔄 modify-ids", "Modify telemetry IDs (VS Code-based editors)"),
        ("🚀 all", "Run all operations (complete optimization)"),
    ]
    
    for cmd, desc in commands:
        click.echo(click.style(f"  • augment-vip {cmd.split()[1]}", fg='green', bold=True))
        click.echo(click.style(f"    {desc}", fg='white', dim=True))
        click.echo()
    
    click.echo(click.style("🎯 Example Usage:", fg='yellow', bold=True))
    click.echo(click.style("  augment-vip clean --auto      # Clean all detected IDEs", fg='white'))
    click.echo(click.style("  augment-vip clean --ide vscode # Clean specific IDE", fg='white'))
    click.echo(click.style("  augment-vip all               # Interactive complete optimization", fg='white'))

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except Exception as e:
        click.echo(click.style(f"💥 Unexpected error: {e}", fg='red', bold=True))
        sys.exit(1)

if __name__ == "__main__":
    main()
