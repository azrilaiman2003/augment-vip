# Augment VIP

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

A universal utility toolkit for VIP users, providing tools to manage and clean multiple IDE databases and configurations. Now with support for VS Code, IntelliJ IDEA, Cursor, and other popular editors!

Tested on Mac Os with VS Code, Cursor, and IntelliJ IDEA
Status : Working
Last Tested : 4 June 2025 1:50PM GMT8+

## 🚀 Features

- **Multi-IDE Support**: Works with VS Code, VS Code Insiders, Cursor, VSCodium, IntelliJ IDEA, PyCharm, WebStorm, PhpStorm
- **Interactive IDE Selection**: Choose your IDE from a terminal-based selector
- **Database Cleaning**: Remove target entries from IDE databases and configuration files
- **Telemetry ID Modification**: Generate random telemetry IDs for VS Code-based editors to enhance privacy
- **Auto-Detection**: Automatically detect and process all installed supported IDEs
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Python-Based**: Uses Python for better cross-platform compatibility
- **Virtual Environment**: Isolates dependencies to avoid conflicts
- **Safe Operations**: Creates backups before making any changes
- **User-Friendly**: Clear, color-coded output and detailed status messages

## 📋 Requirements

- Python 3.6 or higher
- No external system dependencies required (all managed through Python)

## 💻 Installation

### One-Line Install

You can install with a single command using curl:

```bash
curl -fsSL https://raw.githubusercontent.com/azrilaiman2003/augment-vip/development/install.sh -o install.sh && chmod +x install.sh && ./install.sh
```

This will:
1. Download the installation script
2. Make it executable
3. Check for Python 3.6 or higher
4. Create a new `augment-vip` directory in your current location
5. Download the Python installer and package files
6. Set up a Python virtual environment
7. Install the package in the virtual environment
8. Detect your installed IDEs and prompt for operations
9. Run the selected tools automatically

### Installation Options

You can also run the installation script with options to automatically run the cleaning and ID modification tools:

```bash
# Install and run database cleaning on all detected IDEs
curl -fsSL https://raw.githubusercontent.com/azrilaiman2003/augment-vip/python/install.sh -o install.sh && chmod +x install.sh && ./install.sh --clean

# Install and modify telemetry IDs for all supported IDEs
curl -fsSL https://raw.githubusercontent.com/azrilaiman2003/augment-vip/python/install.sh -o install.sh && chmod +x install.sh && ./install.sh --modify-ids

# Install and run all tools on all detected IDEs
curl -fsSL https://raw.githubusercontent.com/azrilaiman2003/augment-vip/python/install.sh -o install.sh && chmod +x install.sh && ./install.sh --all

# Show help
curl -fsSL https://raw.githubusercontent.com/azrilaiman2003/augment-vip/python/install.sh -o install.sh && chmod +x install.sh && ./install.sh --help
```

### Repository Install

If you prefer to clone the entire repository:

```bash
git clone https://github.com/azrilaiman2003/augment-vip.git
cd augment-vip
python install.py
```

### Manual Installation

If you prefer to set up manually:

```bash
# Clone the repository
git clone https://github.com/azrilaiman2003/augment-vip.git
cd augment-vip

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install the package
pip install -e .
```

## 🔧 Usage

### List Supported IDEs

To see all supported IDEs and their installation status:

```bash
# If using the virtual environment (recommended)
.venv/bin/augment-vip list-ides  # macOS/Linux
.venv\Scripts\augment-vip list-ides  # Windows

# If installed globally
augment-vip list-ides
```

### Interactive IDE Selection

For an interactive experience, simply run commands without parameters:

```bash
# Clean databases with interactive IDE selection
augment-vip clean

# Modify telemetry IDs with interactive IDE selection
augment-vip modify-ids

# Run all tools with interactive IDE selection
augment-vip all
```

### Clean IDE Databases

To remove target entries from IDE databases:

```bash
# Interactive selection
augment-vip clean

# Auto-detect and clean all supported IDEs
augment-vip clean --auto

# Clean a specific IDE
augment-vip clean --ide vscode
augment-vip clean --ide cursor
augment-vip clean --ide intellij
```

This will:
- Detect your operating system and installed IDEs
- Find IDE database/configuration files
- Create backups of each file
- Remove target entries from the databases/configs
- Report the results

**Supported for cleaning**: VS Code, VS Code Insiders, Cursor, VSCodium, IntelliJ IDEA, PyCharm, WebStorm, PhpStorm

### Modify IDE Telemetry IDs

To change the telemetry IDs for VS Code-based editors:

```bash
# Interactive selection
augment-vip modify-ids

# Auto-detect and modify all supported IDEs
augment-vip modify-ids --auto

# Modify a specific IDE
augment-vip modify-ids --ide vscode
augment-vip modify-ids --ide cursor
```

This will:
- Locate the IDE's storage.json file
- Generate a random 64-character hex string for machineId
- Generate a random UUID v4 for devDeviceId
- Create a backup of the original file
- Update the file with the new random values

**Supported for telemetry modification**: VS Code, VS Code Insiders, Cursor, VSCodium

### Run All Tools

To run all supported tools:

```bash
# Interactive selection
augment-vip all

# Auto-detect and process all supported IDEs
augment-vip all --auto

# Process a specific IDE
augment-vip all --ide vscode
```

## 📋 Examples

### Example 1: Quick Start - Clean All IDEs

```bash
# Install and immediately clean all detected IDEs
curl -fsSL https://raw.githubusercontent.com/azrilaiman2003/augment-vip/development/install.sh | bash -s -- --clean
```

### Example 2: Interactive IDE Selection

```bash
# Run the tool and choose your IDE from the menu
augment-vip clean

# Output:
# ==================================================
# AUGMENT VIP - IDE SELECTOR
# ==================================================
# Detected IDEs:
# 1. Visual Studio Code
#    Path: /Users/user/Library/Application Support/Code/User
#    Operations: clean, modify_ids
# 
# 2. Cursor
#    Path: /Users/user/Library/Application Support/Cursor/User
#    Operations: clean, modify_ids
# 
# 0. Cancel
# --------------------------------------------------
# Select an IDE (enter number): 1
```

### Example 3: Batch Processing

```bash
# Clean all detected IDEs automatically
augment-vip clean --auto

# Modify telemetry IDs for all VS Code-based editors
augment-vip modify-ids --auto

# Run everything on all detected IDEs
augment-vip all --auto
```

### Example 4: Specific IDE Operations

```bash
# Clean only VS Code
augment-vip clean --ide vscode

# Modify Cursor telemetry IDs
augment-vip modify-ids --ide cursor

# Process IntelliJ IDEA (cleaning only, no telemetry modification)
augment-vip clean --ide intellij
```

### Example 5: Check IDE Support

```bash
# See all supported IDEs and which ones are installed
augment-vip list-ides

# Output:
# Visual Studio Code (vscode)
#   Status: ✅ Installed
#   Path: /Users/user/Library/Application Support/Code/User
#   Operations: clean, modify_ids
# 
# Cursor (cursor)
#   Status: ✅ Installed
#   Path: /Users/user/Library/Application Support/Cursor/User
#   Operations: clean, modify_ids
# 
# IntelliJ IDEA (intellij)
#   Status: ❌ Not Found
#   Path: N/A
#   Operations: clean
```

## 📁 Project Structure

```
augment-vip/
├── .venv/                  # Virtual environment (created during installation)
├── augment_vip/            # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── db_cleaner.py       # Database cleaning functionality
│   ├── id_modifier.py      # Telemetry ID modification functionality
│   └── utils.py            # Utility functions
├── install.py              # Python installation script
├── install.sh              # Bash wrapper for Python installer
├── README.md               # This file
├── requirements.txt        # Package dependencies
└── setup.py                # Package setup script
```

## 🔍 How It Works

The multi-IDE cleaning tool works by:

1. **IDE Detection**: Automatically detects installed IDEs on your system (VS Code, Cursor, IntelliJ IDEA, etc.).

2. **Path Resolution**: Finds the correct configuration and database paths for each IDE based on your operating system.

3. **Creating Backups**: Before making any changes, the tool creates a backup of each file.

4. **Cleaning Process**: 
   - **VS Code-based editors**: Uses SQLite commands to remove target entries from `.vscdb` databases
   - **JetBrains IDEs**: Parses and cleans XML configuration files to remove target references

5. **Reporting Results**: Provides detailed feedback about the operations performed on each IDE.

## 🎯 Supported IDEs

### VS Code-Based Editors (Full Support)
These editors support both database cleaning and telemetry ID modification:

- **Visual Studio Code** (`vscode`) - The original Microsoft VS Code
- **Visual Studio Code Insiders** (`vscode-insiders`) - Preview builds of VS Code
- **Cursor** (`cursor`) - AI-powered code editor based on VS Code
- **VSCodium** (`codium`) - Open-source binaries of VS Code

### JetBrains IDEs (Cleaning Only)
These editors support database/configuration cleaning but not telemetry ID modification:

- **IntelliJ IDEA** (`intellij`) - Java and multi-language IDE
- **PyCharm** (`pycharm`) - Python development environment
- **WebStorm** (`webstorm`) - JavaScript and web development IDE
- **PhpStorm** (`phpstorm`) - PHP development environment

The tool automatically detects supported IDE versions from 2024.1 to 2024.3. If you have a different version, the paths in `utils.py` can be easily updated.

## 🛠️ Troubleshooting

### Common Issues

**Python Not Found**
```
[ERROR] Python 3 is not installed or not in PATH
```
Install Python 3.6 or higher:
- Windows: Download from https://www.python.org/downloads/
- macOS: `brew install python3` or download from https://www.python.org/downloads/
- Ubuntu/Debian: `sudo apt install python3 python3-venv`
- Fedora/RHEL: `sudo dnf install python3 python3-venv`

**Permission Denied**
```
[ERROR] Permission denied
```
Make sure the scripts are executable:
```bash
chmod +x install.sh
```

**No Databases Found**
```
[WARNING] No database files found
```
This may occur if you haven't used VS Code on your system, or if it's installed in non-standard locations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

Azril Aiman - me@azrilaiman.my

Project Link: [https://github.com/azrilaiman2003/augment-vip](https://github.com/azrilaiman2003/augment-vip)

---

Made with ❤️ by [Azril Aiman](https://github.com/azrilaiman2003)
