#!/usr/bin/env bash
#
# install.sh
#
# Description: Installation script for the Augment VIP project (Python version)
# This script downloads and runs the Python-based installer
#
# Usage: ./install.sh [options]
#   Options:
#     --help          Show this help message
#     --clean         Run database cleaning script after installation
#     --modify-ids    Run telemetry ID modification script after installation
#     --all           Run all scripts (clean and modify IDs)

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Text formatting
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

# Repository information
REPO_URL="https://raw.githubusercontent.com/azrilaiman2003/augment-vip/development"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for Python
check_python() {
    log_info "Checking for Python..."

    # Try python3 first, then python as fallback
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        log_success "Found Python 3: $(python3 --version)"
    elif command -v python &> /dev/null; then
        # Check if python is Python 3
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
            PYTHON_CMD="python"
            log_success "Found Python 3: $PYTHON_VERSION"
        else
            log_error "Python 3 is required but found: $PYTHON_VERSION"
            log_info "Please install Python 3.6 or higher from https://www.python.org/downloads/"
            exit 1
        fi
    else
        log_error "Python 3 is not installed or not in PATH"
        log_info "Please install Python 3.6 or higher from https://www.python.org/downloads/"
        exit 1
    fi
}

# Download Python installer
download_python_installer() {
    log_info "Downloading Python installer..."

    # Create a project directory for standalone installation
    PROJECT_ROOT="$SCRIPT_DIR/augment-vip"
    log_info "Creating project directory at: $PROJECT_ROOT"
    mkdir -p "$PROJECT_ROOT"

    # Download the Python installer
    INSTALLER_URL="$REPO_URL/install.py"
    INSTALLER_PATH="$PROJECT_ROOT/install.py"

    log_info "Downloading from: $INSTALLER_URL"
    log_info "Saving to: $INSTALLER_PATH"

    # Use -L to follow redirects
    if curl -L "$INSTALLER_URL" -o "$INSTALLER_PATH"; then
        log_success "Downloaded Python installer"
    else
        log_error "Failed to download Python installer"
        exit 1
    fi

    # Make it executable
    chmod +x "$INSTALLER_PATH"

    # Download the Python package files
    log_info "Downloading Python package files..."

    # Create package directories
    mkdir -p "$PROJECT_ROOT/augment_vip"

    # List of Python files to download
    PYTHON_FILES=(
        "augment_vip/__init__.py"
        "augment_vip/utils.py"
        "augment_vip/db_cleaner.py"
        "augment_vip/id_modifier.py"
        "augment_vip/cli.py"
        "setup.py"
        "requirements.txt"
    )

    # Download each file
    for file in "${PYTHON_FILES[@]}"; do
        file_url="$REPO_URL/$file"
        file_path="$PROJECT_ROOT/$file"

        # Create directory if needed
        mkdir -p "$(dirname "$file_path")"

        log_info "Downloading $file..."

        # Use -L to follow redirects
        if curl -L "$file_url" -o "$file_path"; then
            log_success "Downloaded $file"
        else
            log_warning "Failed to download $file, will try to continue anyway"
        fi
    done

    log_success "All Python files downloaded"
    return 0
}

# Run Python installer
run_python_installer() {
    log_info "Running Python installer..."

    # Change to the project directory
    cd "$PROJECT_ROOT"

    # Run the Python installer with the provided arguments
    if "$PYTHON_CMD" install.py "$@"; then
        log_success "Python installation completed successfully"
    else
        log_error "Python installation failed"
        exit 1
    fi

    # Return to the original directory
    cd - > /dev/null
}

# Display help message
show_help() {
    echo "Augment VIP Installation Script (Multi-IDE Version)"
    echo
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --help          Show this help message"
    echo "  --clean         Run database cleaning on all detected IDEs after installation"
    echo "  --modify-ids    Run telemetry ID modification on all supported IDEs after installation"
    echo "  --all           Run all tools on all detected IDEs"
    echo
    echo "Supported IDEs:"
    echo "  - Visual Studio Code, VS Code Insiders, Cursor, VSCodium (full support)"
    echo "  - IntelliJ IDEA, PyCharm, WebStorm, PhpStorm (cleaning only)"
    echo
    echo "Example: $0 --all"
}

# Run IDE detection and user prompts
run_ide_operations() {
    local operation="$1"
    
    # Get the path to the augment-vip command
    if [ "$PYTHON_CMD" = "python3" ]; then
        AUGMENT_CMD="$PROJECT_ROOT/.venv/bin/augment-vip"
    else
        if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
            AUGMENT_CMD="$PROJECT_ROOT/.venv/Scripts/augment-vip.exe"
        else
            AUGMENT_CMD="$PROJECT_ROOT/.venv/bin/augment-vip"
        fi
    fi

    # First, show what IDEs are installed
    echo
    log_info "Scanning for installed IDEs..."
    "$AUGMENT_CMD" list-ides

    echo
    case "$operation" in
        "clean")
            log_info "Database cleaning will remove target entries from IDE databases and configuration files."
            echo
            read -p "Would you like to clean all detected IDEs automatically? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log_info "Running automatic database cleaning on all detected IDEs..."
                "$AUGMENT_CMD" clean --auto
            else
                echo
                read -p "Would you like to select an IDE interactively? (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Running interactive IDE selection for cleaning..."
                    "$AUGMENT_CMD" clean
                fi
            fi
            ;;
        "modify-ids")
            log_info "Telemetry ID modification will generate new random IDs for VS Code-based editors."
            echo
            read -p "Would you like to modify telemetry IDs for all supported IDEs automatically? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log_info "Running automatic telemetry ID modification on all supported IDEs..."
                "$AUGMENT_CMD" modify-ids --auto
            else
                echo
                read -p "Would you like to select an IDE interactively? (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Running interactive IDE selection for telemetry ID modification..."
                    "$AUGMENT_CMD" modify-ids
                fi
            fi
            ;;
        "all")
            log_info "This will run all supported operations on detected IDEs."
            echo
            read -p "Would you like to process all detected IDEs automatically? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log_info "Running all operations on all detected IDEs..."
                "$AUGMENT_CMD" all --auto
            else
                echo
                read -p "Would you like to select an IDE interactively? (y/n) " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Running interactive IDE selection for all operations..."
                    "$AUGMENT_CMD" all
                fi
            fi
            ;;
    esac
}

# Main installation function
main() {
    # Parse command line arguments
    INSTALL_CLEAN=false
    INSTALL_MODIFY_IDS=false
    INSTALL_ALL=false

    for arg in "$@"; do
        case "$arg" in
            "--help")
                show_help
                exit 0
                ;;
            "--clean")
                INSTALL_CLEAN=true
                ;;
            "--modify-ids")
                INSTALL_MODIFY_IDS=true
                ;;
            "--all")
                INSTALL_ALL=true
                ;;
        esac
    done

    log_info "Starting installation process for Augment VIP (Multi-IDE Version)"

    # Check for Python
    check_python

    # Download Python installer
    download_python_installer

    # Run Python installer with --no-prompt to avoid double prompting
    run_python_installer --no-prompt

    # Get the path to the augment-vip command
    if [ "$PYTHON_CMD" = "python3" ]; then
        AUGMENT_CMD="$PROJECT_ROOT/.venv/bin/augment-vip"
    else
        if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* ]]; then
            AUGMENT_CMD="$PROJECT_ROOT/.venv/Scripts/augment-vip.exe"
        else
            AUGMENT_CMD="$PROJECT_ROOT/.venv/bin/augment-vip"
        fi
    fi

    # Handle command line options
    if [ "$INSTALL_ALL" = true ]; then
        log_info "Running all operations on all detected IDEs (from --all flag)..."
        "$AUGMENT_CMD" all --auto
    elif [ "$INSTALL_CLEAN" = true ]; then
        log_info "Running database cleaning on all detected IDEs (from --clean flag)..."
        "$AUGMENT_CMD" clean --auto
    elif [ "$INSTALL_MODIFY_IDS" = true ]; then
        log_info "Running telemetry ID modification on all supported IDEs (from --modify-ids flag)..."
        "$AUGMENT_CMD" modify-ids --auto
    else
        # Interactive mode - show options
        echo
        echo "============================================================"
        echo "                    AUGMENT VIP INSTALLED"
        echo "============================================================"
        echo
        log_success "Installation completed successfully!"
        
        # Show detected IDEs
        "$AUGMENT_CMD" list-ides
        
        echo
        echo "What would you like to do?"
        echo "1) Clean databases on all detected IDEs"
        echo "2) Modify telemetry IDs for supported IDEs"  
        echo "3) Run all operations on detected IDEs"
        echo "4) Exit (you can run commands manually later)"
        echo
        read -p "Enter your choice (1-4): " -n 1 -r
        echo
        echo
        
        case $REPLY in
            1)
                run_ide_operations "clean"
                ;;
            2)
                run_ide_operations "modify-ids"
                ;;
            3)
                run_ide_operations "all"
                ;;
            4)
                log_info "Skipping automatic operations."
                ;;
            *)
                log_warning "Invalid choice. Skipping automatic operations."
                ;;
        esac
    fi

    # Show usage information
    echo
    echo "============================================================"
    echo "                     USAGE INFORMATION"
    echo "============================================================"
    echo
    log_info "You can now use Augment VIP with the following commands:"
    log_info ""
    log_info "List supported IDEs:"
    log_info "  $AUGMENT_CMD list-ides"
    log_info ""
    log_info "Clean databases (interactive):"
    log_info "  $AUGMENT_CMD clean"
    log_info ""
    log_info "Clean all detected IDEs automatically:"
    log_info "  $AUGMENT_CMD clean --auto"
    log_info ""
    log_info "Clean specific IDE:"
    log_info "  $AUGMENT_CMD clean --ide vscode"
    log_info "  $AUGMENT_CMD clean --ide cursor"
    log_info "  $AUGMENT_CMD clean --ide intellij"
    log_info ""
    log_info "Modify telemetry IDs (VS Code-based editors):"
    log_info "  $AUGMENT_CMD modify-ids"
    log_info "  $AUGMENT_CMD modify-ids --auto"
    log_info ""
    log_info "Run all operations:"
    log_info "  $AUGMENT_CMD all"
    log_info "  $AUGMENT_CMD all --auto"
    echo
}

# Execute main function
main "$@"
