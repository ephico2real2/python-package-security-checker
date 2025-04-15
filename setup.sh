#!/usr/bin/env bash

# Python Package Security Checker - Setup Script
# This script creates a virtual environment and installs all dependencies

# Set error handling
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print with color
print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_colored "$RED" "Error: Python 3 is not installed or not in PATH."
    print_colored "$YELLOW" "Please install Python 3.7 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python_min_version="3.7"

if [[ "$(printf '%s\n' "$python_min_version" "$python_version" | sort -V | head -n1)" != "$python_min_version" ]]; then
    print_colored "$RED" "Error: Python 3.7 or higher is required. Found version: $python_version"
    exit 1
fi

# Create virtual environment
print_colored "$GREEN" "Creating virtual environment..."

# Check if virtualenv directory already exists
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    print_colored "$YELLOW" "Virtual environment directory already exists."
    read -p "Do you want to remove and recreate it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_colored "$YELLOW" "Using existing virtual environment."
    else
        print_colored "$YELLOW" "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        print_colored "$GREEN" "Created new virtual environment."
    fi
else
    python3 -m venv "$VENV_DIR"
    print_colored "$GREEN" "Created new virtual environment."
fi

# Activate virtual environment
print_colored "$GREEN" "Activating virtual environment..."

# Source bashrc if it exists to ensure proper PYTHONPATH and other env variables
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
fi

# Determine activate script based on shell
if [[ "$SHELL" == *"zsh"* ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
else
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
fi

# Activate the virtual environment
source "$ACTIVATE_SCRIPT"

# Check if activation was successful
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_colored "$RED" "Failed to activate virtual environment."
    print_colored "$YELLOW" "Try activating manually with: source $ACTIVATE_SCRIPT"
    exit 1
fi

print_colored "$GREEN" "Virtual environment activated."

# Check if script_requirements.txt exists
if [ ! -f "script_requirements.txt" ]; then
    print_colored "$YELLOW" "Warning: script_requirements.txt not found."
    print_colored "$YELLOW" "Downloading script_requirements.txt..."
    curl -s -O https://raw.githubusercontent.com/ephico2real2/python-package-security-checker/main/script_requirements.txt
    
    if [ ! -f "script_requirements.txt" ]; then
        print_colored "$RED" "Error: Failed to download script_requirements.txt."
        exit 1
    fi
fi

# Install dependencies
print_colored "$GREEN" "Installing dependencies..."
pip install --upgrade pip
pip install -r script_requirements.txt

# Check if security_check.py exists
if [ ! -f "security_check.py" ]; then
    print_colored "$YELLOW" "Warning: security_check.py not found."
    print_colored "$YELLOW" "Downloading security_check.py..."
    curl -s -O https://raw.githubusercontent.com/ephico2real2/python-package-security-checker/main/security_check.py
    
    if [ ! -f "security_check.py" ]; then
        print_colored "$RED" "Error: Failed to download security_check.py."
        exit 1
    else
        chmod +x security_check.py
    fi
fi

# Success message and usage instructions
print_colored "$GREEN" "Setup completed successfully!"
print_colored "$GREEN" "======================="
print_colored "$YELLOW" "To activate the virtual environment in the future, run:"
print_colored "$NC" "    source $VENV_DIR/bin/activate"
print_colored "$YELLOW" "To run the security checker:"
print_colored "$NC" "    python security_check.py -r your-requirements.txt"
print_colored "$YELLOW" "To exit the virtual environment when finished:"
print_colored "$NC" "    deactivate"

