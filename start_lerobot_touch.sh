#!/bin/bash

# ============================================================================
# 🤖 LeRobot Touch UI Launcher - Perfect for 7" touchscreens!
# ============================================================================
# Optimized for Coofun Mini-PC + 7" touch display setups
# No keyboard/mouse required - pure touch control!
# ============================================================================

# Colors for terminal output (in case someone sees it)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              🤖 LeRobot Touch UI Launcher 🤖                         ║"
echo "║                 Optimized for 7\" Touchscreens!                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Make all scripts executable (fix Decepticon clipboard issues!)
# ============================================================================
echo -e "${BLUE}[1/4] 🔧 Setting up permissions...${NC}"

chmod +x update_lerobot_fork.sh 2>/dev/null
chmod +x start_lerobot_ui.sh 2>/dev/null  
chmod +x lerobot_teleop_ui.py 2>/dev/null
chmod +x lerobot_bimanual_ui.py 2>/dev/null
chmod +x lerobot_touch_ui.py 2>/dev/null

echo -e "  ${GREEN}✓ All scripts now executable${NC}"

# ============================================================================
# Find and initialize conda
# ============================================================================
echo -e "${BLUE}[2/4] 🔍 Finding conda...${NC}"

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
    echo "Please install Miniconda first"
    exit 1
fi

# ============================================================================
# Initialize conda for this session
# ============================================================================
echo -e "${BLUE}[3/4] 🐍 Activating LeRobot environment...${NC}"

# Source conda setup
if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
    source "$CONDA_PATH/etc/profile.d/conda.sh"
else
    export PATH="$CONDA_PATH/bin:$PATH"
fi

# Activate lerobot environment
if conda env list | grep -q "^lerobot "; then
    conda activate lerobot
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓ LeRobot environment activated${NC}"
    else
        echo -e "  ${RED}❌ Failed to activate lerobot environment${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}❌ LeRobot environment not found!${NC}"
    echo "Please run: conda create -n lerobot python=3.10"
    exit 1
fi

# ============================================================================
# Launch Touch UI
# ============================================================================
echo -e "${BLUE}[4/4] 🚀 Starting Touch UI...${NC}"

# Check display environment
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo -e "${YELLOW}⚠️  No display detected. Setting DISPLAY=:0${NC}"
    export DISPLAY=:0
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎮 Touch UI Starting! 🎮                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Touch Interface Features:${NC}"
echo "  🤖🤖 Auto-detects bi-manual setups"
echo "  🎮 Big touch-friendly buttons"  
echo "  🤝 Coordination mode selection"
echo "  📱 Perfect for 7\" screens"
echo "  🔧 No keyboard needed!"
echo ""

# Use the Python from the lerobot environment
PYTHON_PATH="$CONDA_PATH/envs/lerobot/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${YELLOW}⚠️ Using system python${NC}"
    PYTHON_PATH="python"
fi

# Launch the Touch UI
echo -e "${CYAN}Launching touch interface...${NC}"
$PYTHON_PATH lerobot_touch_ui.py

# Check exit status
EXIT_CODE=$?
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Touch UI closed normally${NC}"
else
    echo -e "${RED}❌ Touch UI exited with error (code: $EXIT_CODE)${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check that your display is working"
    echo "  2. Ensure tkinter is installed: pip install tk"
    echo "  3. Try terminal mode instead: ./start_lerobot_ui.sh"
    echo "  4. Check USB connections for robots"
fi

echo -e "${CYAN}Thank you for using LeRobot Touch! 🤖${NC}"