# Augment-VIP GUI Version

A simplified, user-friendly GUI version of Augment VIP for managing VS Code configurations.

## Features

- 🎨 **Modern GUI Interface** - Beautiful PyQt6-based interface with animated gradient title
- 🌍 **Bilingual Support** - English and Chinese language support
- 🔧 **One-Click Operations** - Easy-to-use buttons for all functions
- 🎯 **Simplified Setup** - No complex virtual environment setup required

## Functions

1. **Fix All VS Code Configuration** - Closes VS Code and runs all cleaning operations
2. **Close VS Code** - Safely closes all VS Code processes
3. **Clean VS Code Database** - Removes Augment-related entries from VS Code database
4. **Modify VS Code Telemetry ID** - Changes telemetry IDs to random values

## Quick Start

### Windows
1. Double-click `run_gui.bat`
2. The script will automatically install dependencies if needed
3. The GUI will launch automatically

### Manual Start
1. Install dependencies:
   ```bash
   pip install PyQt6 psutil
   ```

2. Run the GUI:
   ```bash
   python run_gui.py
   ```

## Requirements

- Python 3.6 or higher
- PyQt6
- psutil

## File Structure

- `gui_main.py` - Main GUI application
- `core_functions.py` - Core functionality (simplified from original)
- `run_gui.py` - Launcher script with dependency checking
- `run_gui.bat` - Windows batch file for easy launching
- `requirements_gui.txt` - Python dependencies

## Changes from Original

- ✅ Removed complex virtual environment setup
- ✅ Simplified to essential functions only
- ✅ Added modern GUI interface
- ✅ Added bilingual support
- ✅ Added one-click "fix all" functionality
- ✅ Improved user experience with progress indicators

## Version

v0.0.1 - Initial GUI release

## License

MIT License
