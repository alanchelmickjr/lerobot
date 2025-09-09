#!/bin/bash

# ============================================================================
# 🤖 LeRobot Teleoperation Launcher - No manual conda nonsense!
# ============================================================================
# This script automatically:
#   1. Sources conda
#   2. Activates lerobot environment
#   3. Launches the teleoperation UI
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                 🤖 LeRobot Teleoperation Launcher 🤖                 ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# STEP 1: Find and source conda
# ============================================================================
echo -e "${BLUE}[1/3] 🔍 Finding conda...${NC}"

# Check common conda locations
CONDA_FOUND=false
CONDA_PATH=""

# Check for existing conda in PATH
if command -v conda &> /dev/null; then
    CONDA_PATH=$(dirname $(dirname $(which conda)))
    CONDA_FOUND=true
    echo -e "  ${GREEN}✓ Found conda in PATH: $CONDA_PATH${NC}"
else
    # Check common locations
    for conda_dir in ~/miniconda3 ~/anaconda3 ~/miniforge3 ~/mambaforge /opt/miniconda3; do
        if [ -f "$conda_dir/bin/conda" ]; then
            CONDA_PATH="$conda_dir"
            CONDA_FOUND=true
            echo -e "  ${GREEN}✓ Found conda at: $CONDA_PATH${NC}"
            break
        fi
    done
fi

if [ "$CONDA_FOUND" = false ]; then
    echo -e "  ${RED}❌ Conda not found!${NC}"
    echo ""
    echo "Please install Miniconda first by running:"
    echo "  ./setup_lerobot_complete.sh"
    exit 1
fi

# ============================================================================
# STEP 2: Initialize conda for this session
# ============================================================================
echo -e "${BLUE}[2/3] 🔧 Initializing conda...${NC}"

# Source conda setup
if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
    source "$CONDA_PATH/etc/profile.d/conda.sh"
    echo -e "  ${GREEN}✓ Conda initialized${NC}"
else
    # Fallback: add to PATH
    export PATH="$CONDA_PATH/bin:$PATH"
    echo -e "  ${YELLOW}⚠ Using PATH method${NC}"
fi

# ============================================================================
# STEP 3: Activate lerobot environment
# ============================================================================
echo -e "${BLUE}[3/3] 🤖 Activating LeRobot environment...${NC}"

# Check if lerobot environment exists
if conda env list | grep -q "^lerobot "; then
    conda activate lerobot
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓ LeRobot environment activated${NC}"
    else
        echo -e "  ${RED}❌ Failed to activate lerobot environment${NC}"
        echo ""
        echo "Try running: conda activate lerobot"
        exit 1
    fi
else
    echo -e "  ${RED}❌ LeRobot environment not found!${NC}"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup_lerobot_complete.sh"
    exit 1
fi

# ============================================================================
# LAUNCH THE UI
# ============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🚀 Launching Teleoperation UI 🚀                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Make the UI script executable if it isn't
chmod +x lerobot_teleop_ui.py 2>/dev/null

# Use the Python from the lerobot environment specifically
PYTHON_PATH="$CONDA_PATH/envs/lerobot/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${YELLOW}⚠ Python not found in lerobot env, trying default python${NC}"
    PYTHON_PATH="python"
fi

# Launch the Python UI with the correct Python
$PYTHON_PATH lerobot_teleop_ui.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}❌ UI exited with error${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Make sure both SO101 arms are connected"
    echo "  2. Check USB permissions: ls -l /dev/tty.usb*"
    echo "  3. Try running manually:"
    echo "     conda activate lerobot"
    echo "     python lerobot_teleop_ui.py"
fi