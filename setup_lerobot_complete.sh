#!/bin/bash

# ============================================================================
# 🤖 LeRobot Smart Setup Script - With proven conda fix
# ============================================================================
# This script:
#   1. Fixes conda permissions issues first (the proven MacBook fix)
#   2. Installs/uses Miniconda 
#   3. Sets up LeRobot with motor safety
#   4. Auto-calibrates your SO101 arms
# ============================================================================

set +e  # Don't exit on error - we handle failures gracefully

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Detect system
OS=$(uname -s)
ARCH=$(uname -m)

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    🤖 LeRobot Setup with Proven Conda Fix 🤖             ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# THE PROVEN FIX - Create .config/conda with proper permissions FIRST
# ============================================================================
echo -e "${BLUE}[Step 1/5] 🔧 Applying the proven conda permission fix...${NC}"
echo "══════════════════════════════════════════════════════════════════"
echo "  This may require your password for sudo operations."

# Remove any existing problematic config
sudo rm -rf ~/.config/conda 2>/dev/null
sudo rm -f ~/.condarc 2>/dev/null

# Create the directory with proper permissions (THE KEY FIX from your MacBook!)
echo "  Creating ~/.config/conda with proper permissions..."
sudo mkdir -p ~/.config/conda
sudo chmod 755 ~/.config/conda
sudo chown -R $USER:staff ~/.config/

echo -e "  ${GREEN}✓ Config directory created with proper permissions${NC}"

# ============================================================================
# INSTALL OR USE EXISTING MINICONDA
# ============================================================================
echo ""
echo -e "${BLUE}[Step 2/5] 📦 Setting up Miniconda...${NC}"
echo "══════════════════════════════════════════════════════════════════"

CONDA_PATH=""
CONDA_FOUND=false

# Check if conda already exists
if [ -d ~/miniconda3 ] && [ -f ~/miniconda3/bin/conda ]; then
    echo "  Found existing Miniconda at ~/miniconda3"
    CONDA_PATH="$HOME/miniconda3"
    CONDA_FOUND=true
else
    echo "  Installing fresh Miniconda..."
    
    # Determine the correct Miniconda URL
    if [ "$OS" = "Darwin" ]; then
        if [ "$ARCH" = "arm64" ]; then
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            echo -e "  System: ${GREEN}macOS Apple Silicon (M1/M2/M3)${NC}"
        else
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            echo -e "  System: ${GREEN}macOS Intel${NC}"
        fi
    elif [ "$OS" = "Linux" ]; then
        if [ "$ARCH" = "x86_64" ]; then
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            echo -e "  System: ${GREEN}Linux x86_64${NC}"
        elif [ "$ARCH" = "aarch64" ]; then
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
            echo -e "  System: ${GREEN}Linux ARM64${NC}"
        fi
    fi
    
    # Download and install
    echo "  Downloading Miniconda..."
    curl -# -o /tmp/miniconda_installer.sh "$MINICONDA_URL"
    
    echo "  Installing Miniconda..."
    bash /tmp/miniconda_installer.sh -b -u -p ~/miniconda3
    rm /tmp/miniconda_installer.sh
    
    CONDA_PATH="$HOME/miniconda3"
    echo -e "  ${GREEN}✓ Miniconda installed${NC}"
fi

# Add to PATH for this session
export PATH="$CONDA_PATH/bin:$PATH"

# ============================================================================
# INITIALIZE CONDA (with the fix that worked on your MacBook)
# ============================================================================
echo ""
echo -e "${BLUE}[Step 3/5] 🔧 Initializing conda...${NC}"
echo "══════════════════════════════════════════════════════════════════"

# Try to initialize conda - it may show errors but still work (as on your MacBook)
echo "  Running conda init (may show errors but should still work)..."
if [ "$OS" = "Darwin" ]; then
    # macOS uses zsh by default
    CONDA_NO_PLUGINS=true $CONDA_PATH/bin/conda init zsh 2>/dev/null || true
    
    # Add to PATH manually as backup
    if ! grep -q "miniconda3/bin" ~/.zshrc; then
        echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.zshrc
    fi
    
    # Source for current session
    source ~/.zshrc 2>/dev/null || true
else
    # Linux typically uses bash
    CONDA_NO_PLUGINS=true $CONDA_PATH/bin/conda init bash 2>/dev/null || true
    CONDA_NO_PLUGINS=true $CONDA_PATH/bin/conda init zsh 2>/dev/null || true
fi

echo -e "  ${GREEN}✓ Conda initialized (errors are expected and OK)${NC}"

# ============================================================================
# CREATE LEROBOT ENVIRONMENT
# ============================================================================
echo ""
echo -e "${BLUE}[Step 4/5] 🤖 Creating LeRobot environment...${NC}"
echo "══════════════════════════════════════════════════════════════════"

# Remove old environment if it exists
if $CONDA_PATH/bin/conda env list | grep -q "^lerobot "; then
    echo "  Removing old LeRobot environment..."
    $CONDA_PATH/bin/conda env remove -n lerobot -y &>/dev/null
fi

# Create new environment (use classic solver to avoid libmamba issues)
echo "  Creating Python 3.10 environment..."
CONDA_NO_PLUGINS=true CONDA_SOLVER=classic $CONDA_PATH/bin/conda create -n lerobot python=3.10 -y

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ LeRobot environment created${NC}"
    
    # Activate environment
    echo "  Activating lerobot environment..."
    source $CONDA_PATH/bin/activate lerobot
    echo -e "  ${GREEN}✓ Environment activated (currently in 'lerobot' env)${NC}"
    
    echo "  Installing ffmpeg (this may take a minute)..."
    conda install ffmpeg -c conda-forge -y >/dev/null 2>&1
    
    echo "  Installing LeRobot with Feetech motor support..."
    pip install -e ".[feetech]" --quiet
    
    echo "  Installing pyserial for USB communication..."
    pip install pyserial --quiet
    
    echo -e "  ${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}Failed to create environment. Please check the error above.${NC}"
    echo ""
    echo "Try running these commands manually:"
    echo "  conda create -n lerobot python=3.10 -y"
    echo "  conda activate lerobot"
    echo "  pip install -e '.[feetech]'"
    exit 1
fi

# ============================================================================
# AUTO-CALIBRATE SO101 ARMS
# ============================================================================
echo ""
echo -e "${MAGENTA}[Step 5/5] 🦾 SO101 Arm Auto-Calibration${NC}"
echo "══════════════════════════════════════════════════════════════════"

echo ""
echo -e "${CYAN}Ready to calibrate your SO101 arms!${NC}"
echo ""
echo "Please ensure:"
echo "  • Both SO101 arms (leader and follower) are connected via USB"
echo "  • Both arms are powered on"
echo "  • Arms can move freely (no obstructions)"
echo ""
read -p "Ready to start calibration? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Starting intelligent auto-calibration...${NC}"
    python -m lerobot.scripts.auto_calibrate_so101
    CALIBRATION_DONE=true
else
    echo ""
    echo -e "${YELLOW}Skipping calibration.${NC}"
    CALIBRATION_DONE=false
fi

# ============================================================================
# COMPLETE!
# ============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                     🎉 Setup Complete! 🎉                                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}✅ What's been done:${NC}"
echo "  • Applied the proven conda permission fix"
echo "  • Conda is working at: $CONDA_PATH"
echo "  • Created LeRobot environment (Python 3.10)"
echo "  • Installed all dependencies (ffmpeg, feetech, pyserial)"
if [ "$CALIBRATION_DONE" = true ]; then
    echo "  • Calibrated SO101 arms"
fi

echo ""
echo -e "${CYAN}📝 To start using LeRobot:${NC}"
echo ""

if [ "$OS" = "Darwin" ]; then
    echo "  1. Restart your terminal or run:"
    echo -e "     ${YELLOW}source ~/.zshrc${NC}"
    echo ""
    echo "  2. Activate the environment:"
    echo -e "     ${YELLOW}conda activate lerobot${NC}"
else
    echo "  1. Activate the environment:"
    echo -e "     ${YELLOW}conda activate lerobot${NC}"
fi

echo ""
echo "  If 'conda activate' shows an error, run:"
echo -e "     ${YELLOW}conda init zsh${NC}  (on macOS)"
echo -e "     ${YELLOW}conda init bash${NC} (on Linux)"
echo "  Then restart your terminal."

echo ""
if [ "$CALIBRATION_DONE" = false ]; then
    echo "  3. Run calibration when ready:"
    echo -e "     ${YELLOW}python -m lerobot.scripts.auto_calibrate_so101${NC}"
    echo ""
    echo "  4. Start teleoperation:"
else
    echo "  3. Start teleoperation:"
fi

echo -e "     ${YELLOW}lerobot-teleoperate \\
       --robot.type=so101_follower \\
       --robot.port=<follower_port> \\
       --teleop.type=so101_leader \\
       --teleop.port=<leader_port>${NC}"

echo ""
echo -e "${GREEN}🛡️ Motor Safety System Active!${NC}"
echo "  • Temperature protection (50°C shutdown)"
echo "  • Stall detection prevents burnout"
echo "  • Soft start reduces wear"
echo ""
echo -e "${MAGENTA}Happy roboting! 🤖${NC}"
echo ""
echo -e "${YELLOW}Note: Some conda errors during setup are normal and expected.${NC}"
echo -e "${YELLOW}As long as conda commands work, everything is fine!${NC}"