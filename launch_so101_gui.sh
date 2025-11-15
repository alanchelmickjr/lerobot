#!/bin/bash

# SO-101 Robot Control GUI Launcher
# Handles environment setup, permissions, and launching the GUI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    echo -e "${2}${1}${NC}"
}

print_color "🚀 SO-101 Robot Control System Launcher" "$BLUE"
print_color "==========================================" "$BLUE"

# Check if running on Linux (for permissions)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_color "🐧 Linux system detected" "$GREEN"
    
    # Check if we need to fix permissions
    if ls /dev/ttyACM* 2>/dev/null; then
        print_color "📡 Found USB ports:" "$YELLOW"
        ls -la /dev/ttyACM* 2>/dev/null || true
        
        # Check if permissions need fixing
        for port in /dev/ttyACM*; do
            if [ -e "$port" ]; then
                perms=$(stat -c %a "$port")
                if [ "$perms" != "666" ]; then
                    print_color "⚠️  Port $port needs permission fix (current: $perms)" "$YELLOW"
                    print_color "🔧 Fixing permissions (may require sudo password)..." "$YELLOW"
                    sudo chmod 666 "$port"
                    print_color "✅ Fixed permissions for $port" "$GREEN"
                fi
            fi
        done
    else
        print_color "⚠️  No USB ports found. Connect robots first." "$YELLOW"
    fi
fi

# Find conda installation
print_color "\n🔍 Looking for conda installation..." "$BLUE"

CONDA_FOUND=false
CONDA_INIT=""

# Check common conda locations
CONDA_PATHS=(
    "$HOME/miniconda3"
    "$HOME/anaconda3"
    "$HOME/miniforge3"
    "$HOME/mambaforge"
    "/opt/conda"
    "/usr/local/miniconda3"
    "/usr/local/anaconda3"
)

for CONDA_PATH in "${CONDA_PATHS[@]}"; do
    if [ -f "$CONDA_PATH/bin/conda" ]; then
        print_color "✅ Found conda at: $CONDA_PATH" "$GREEN"
        CONDA_FOUND=true
        CONDA_INIT="$CONDA_PATH/bin/conda"
        break
    fi
done

if [ "$CONDA_FOUND" = false ]; then
    print_color "❌ Conda not found! Please install miniconda first." "$RED"
    print_color "Visit: https://docs.conda.io/en/latest/miniconda.html" "$YELLOW"
    exit 1
fi

# Initialize conda
print_color "\n🔧 Initializing conda..." "$BLUE"
eval "$($CONDA_INIT shell.bash hook)"

# Check if lerobot environment exists
if conda env list | grep -q "lerobot"; then
    print_color "✅ Found lerobot environment" "$GREEN"
else
    print_color "❌ LeRobot environment not found!" "$RED"
    print_color "Creating lerobot environment..." "$YELLOW"
    
    # Create environment
    conda create -n lerobot python=3.10 -y
    conda activate lerobot
    
    # Install dependencies
    pip install torch torchvision torchaudio
    pip install pyserial
    pip install pillow
    pip install numpy
    
    # Install lerobot
    if [ -d "/home/feetech/lerobot" ]; then
        cd /home/feetech/lerobot
        pip install -e .
    else
        print_color "⚠️  LeRobot directory not found at /home/feetech/lerobot" "$YELLOW"
        print_color "Please clone LeRobot first:" "$YELLOW"
        print_color "git clone https://github.com/huggingface/lerobot.git" "$YELLOW"
        exit 1
    fi
fi

# Activate lerobot environment
print_color "\n🐍 Activating lerobot environment..." "$BLUE"
conda activate lerobot

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
print_color "📦 Python version: $PYTHON_VERSION" "$GREEN"

# Check if GUI script exists
GUI_SCRIPT="so101_robot_control_gui.py"
if [ ! -f "$GUI_SCRIPT" ]; then
    print_color "❌ GUI script not found: $GUI_SCRIPT" "$RED"
    print_color "Please ensure the script is in the current directory." "$YELLOW"
    exit 1
fi

# Launch the GUI
print_color "\n🚀 Launching SO-101 Robot Control GUI..." "$GREEN"
print_color "==========================================" "$GREEN"

# Run the GUI with proper environment
python "$GUI_SCRIPT"

print_color "\n👋 GUI closed. Goodbye!" "$BLUE"