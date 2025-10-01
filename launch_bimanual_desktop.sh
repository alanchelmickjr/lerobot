#!/bin/bash

# ============================================================================
# 🤖 Desktop Launcher for Bi-Manual Touch UI
# Run this directly on the Coofun Mini-PC desktop (not via SSH)
# ============================================================================

# Colors for terminal output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🤖🤖 Starting Bi-Manual Touch UI...${NC}"

# Find conda
CONDA_FOUND=false
for conda_dir in ~/miniconda3 ~/anaconda3 ~/miniforge3; do
    if [ -f "$conda_dir/bin/conda" ]; then
        CONDA_PATH="$conda_dir"
        CONDA_FOUND=true
        break
    fi
done

if [ "$CONDA_FOUND" = false ]; then
    echo -e "${RED}❌ Conda not found!${NC}"
    exit 1
fi

# Source conda and activate lerobot
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate lerobot

# Set display
export DISPLAY=:0

# Launch from lerobot directory
cd ~/lerobot

echo -e "${GREEN}✅ Launching touch interface...${NC}"
python lerobot_touch_ui.py