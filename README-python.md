# Augment VIP (Python Version)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.0.0-green.svg)

A comprehensive utility toolkit for managing telemetry IDs and cleaning databases across multiple IDEs. This Python version supports JetBrains IDEs, VS Code variants, and provides excellent cross-platform compatibility.

## 🚀 Features

- **Multi-IDE Support**: JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.) and VS Code variants (VS Code, Cursor, VSCodium, etc.)
- **Database Cleaning**: Remove Augment-related entries from VS Code databases
- **Telemetry ID Modification**: Generate random telemetry IDs to enhance privacy
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Python-Based**: Uses Python for better cross-platform compatibility and no external system dependencies
- **Virtual Environment**: Isolates dependencies to avoid conflicts
- **Safe Operations**: Creates backups before making any changes and locks modified files
- **Flexible CLI**: Choose specific IDEs or run on all detected installations
- **Status Detection**: See which IDEs are detected on your system

## 📋 Requirements

- Python 3.6 or higher
- No external system dependencies required (all managed through Python)

## 💻 Installation

### Quick Install

Run the installer script:

```bash
# On macOS/Linux
python3 install.py

# On Windows
python install.py
```

### Installation Options

```bash
# Install and run database cleaning
python install.py --clean

# Install and modify telemetry IDs
python install.py --modify-ids

# Install and run all tools
python install.py --all
```

### Manual Installation

If you prefer to set up manually:

```bash
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

### Check IDE Status

See which IDEs are detected on your system:

```bash
augment-vip status
```

This will show:
- JetBrains configuration directory location
- JetBrains ID files status
- VS Code variant installations found
- Configuration file locations

### Modify Telemetry IDs (All IDEs)

To modify telemetry IDs across all detected IDEs:

```bash
augment-vip modify-ids
```

### Target Specific IDEs

**JetBrains IDEs Only:**
```bash
augment-vip jetbrains
# or
augment-vip modify-ids --jetbrains
```

**VS Code Variants Only:**
```bash
augment-vip vscode
# or
augment-vip modify-ids --vscode
```

**Legacy VS Code Mode (single installation):**
```bash
augment-vip modify-ids --legacy
```

### Clean VS Code Databases

To remove Augment-related entries from VS Code databases:

```bash
augment-vip clean
```

### Run All Tools

**All IDEs:**
```bash
augment-vip all
```

**Specific IDE Types:**
```bash
# JetBrains only
augment-vip all --jetbrains-only

# VS Code variants only
augment-vip all --vscode-only

# Skip database cleaning
augment-vip all --skip-clean
```

## 🎯 Supported IDEs

### JetBrains IDEs
- IntelliJ IDEA (Community & Ultimate)
- PyCharm (Community & Professional)
- WebStorm
- PhpStorm
- CLion
- DataGrip
- GoLand
- RubyMine
- Rider
- AppCode
- And other JetBrains products

### VS Code Variants
- Visual Studio Code
- Visual Studio Code Insiders
- VSCodium
- Cursor
- Windsurf
- Zed
- code-server
- Other VS Code-based editors

## 📁 Project Structure

```
augment-vip/
├── .venv/                  # Virtual environment (created during installation)
├── augment_vip/            # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── db_cleaner.py       # Database cleaning functionality
│   ├── id_modifier.py      # Multi-IDE telemetry ID modification
│   └── utils.py            # Utility functions
├── install.py              # Installation script
├── multi_ide_modifier.py   # Standalone script (equivalent to Rust version)
├── README.md               # Main documentation
├── README-python.md        # This file
├── requirements.txt        # Package dependencies
└── setup.py                # Package setup script
```

## 🔍 How It Works

### JetBrains IDE Support

The tool modifies JetBrains telemetry by:

1. **Finding JetBrains Config**: Searches common configuration directories across platforms
2. **Updating ID Files**: Modifies `PermanentDeviceId` and `PermanentUserId` files
3. **Generating New IDs**: Creates fresh UUID v4 identifiers
4. **Locking Files**: Makes files read-only and protected against modification

### VS Code Variant Support

For VS Code-based editors:

1. **Multi-Variant Detection**: Finds all VS Code variants (VS Code, Cursor, VSCodium, etc.)
2. **Storage Modification**: Updates `storage.json` files with new telemetry IDs
3. **Database Cleaning**: Removes Augment-related entries from state databases
4. **Workspace Support**: Handles both global and workspace-specific configurations

### Database Cleaning

The database cleaning functionality:

1. **Finds Database Files**: Locates SQLite databases in VS Code storage directories
2. **Creates Backups**: Safely backs up databases before modification
3. **Removes Entries**: Uses SQL queries to remove Augment-related data
4. **Processes Backups**: Also cleans backup database files

## 🛠️ Standalone Script

A standalone script `multi_ide_modifier.py` is provided that replicates the exact functionality of the original Rust code:

```bash
# Run standalone script
python multi_ide_modifier.py

# Help
python multi_ide_modifier.py --help
```

This script:
- Requires no installation
- Works independently of the package
- Provides the same multi-IDE support
- Uses base64 encoded strings (like the Rust version)

## 🛠️ Troubleshooting

### Common Issues

**Python Not Found**
```
'python' is not recognized as an internal or external command
```
Make sure Python is installed and added to your PATH.

**Permission Denied**
```
Permission denied
```
On macOS/Linux, you may need to make the scripts executable:
```bash
chmod +x install.py
chmod +x multi_ide_modifier.py
```

**No IDEs Found**
```
No JetBrains or VSCode installations found
```
- Make sure your IDEs are installed in standard locations
- Run `augment-vip status` to see what the tool detects
- Some portable installations may not be detected

**File Locking Issues**
```
Failed to lock file
```
- On Windows: Ensure no antivirus is interfering
- On macOS/Linux: Check file permissions and directory access

**Database Access Issues**
```
Failed to clean database
```
- Ensure VS Code is completely closed
- Check that database files aren't being used by other processes

## 🔧 Command Reference

| Command | Description |
|---------|-------------|
| `augment-vip status` | Show detected IDEs and configuration |
| `augment-vip modify-ids` | Modify all IDE telemetry IDs |
| `augment-vip jetbrains` | JetBrains IDEs only |
| `augment-vip vscode` | VS Code variants only |
| `augment-vip clean` | Clean VS Code databases |
| `augment-vip all` | Run all tools |

### Modify IDs Options

| Option | Description |
|--------|-------------|
| `--jetbrains` | Process JetBrains IDEs only |
| `--vscode` | Process VS Code variants only |
| `--legacy` | Use legacy single VS Code mode |

### All Command Options

| Option | Description |
|--------|-------------|
| `--jetbrains-only` | Process JetBrains IDEs only |
| `--vscode-only` | Process VS Code variants only |
| `--skip-clean` | Skip database cleaning step |

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
