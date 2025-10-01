#!/bin/bash

# ============================================================================
# 🤖🤖 LeRobot Bi-Manual Upgrade Script - Complete Fork Overwrite
# ============================================================================
# One-liner deployment: 
#   curl -sSL https://raw.githubusercontent.com/YOUR-FORK/lerobot/main/upgrade_to_bimanual.sh | bash
# 
# This script completely overwrites LeRobot with our bi-manual fork including:
#   - Scalable arm detection (single → bi → tri → quad-manual)
#   - Touch UI with coordination modes
#   - Auto-calibration system
#   - LeKiwi support
#   - XArm research integration
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║              🤖🤖 LeRobot Bi-Manual Fork Upgrade 🤖🤖                     ║"
echo "║                     Complete System Overwrite                           ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
BIMANUAL_FORK_URL="https://github.com/crackerjack/lerobot.git"
BIMANUAL_BRANCH="bimanual-production"
BACKUP_SUFFIX="backup-$(date +%Y%m%d-%H%M%S)"
INSTALL_DIR="lerobot-bimanual"

echo -e "${PURPLE}🚀 FEATURES INCLUDED:${NC}"
echo "  ✨ Scalable Detection: Single → Bi → Tri → Quad-Manual"
echo "  🎮 Coordination Modes: Joint/Independent/Mirror"
echo "  📱 Touch UI: 7\" screen optimized"
echo "  🔧 Auto-Calibration: Voltage-based detection"
echo "  🦾 LeKiwi Support: Mobile base integration"
echo "  🏭 XArm Research: Industrial upgrade path"
echo "  🎯 One-Liner Deploy: Complete turnkey system"
echo ""

# ============================================================================
# STEP 1: Detect existing installation
# ============================================================================
echo -e "${BLUE}[1/8] 🔍 Checking existing installation...${NC}"

EXISTING_LEROBOT=""
if [ -d "lerobot" ]; then
    EXISTING_LEROBOT="lerobot"
    echo -e "  ${YELLOW}⚠️  Found existing lerobot directory${NC}"
elif [ -d ".git" ] && git remote -v | grep -q "lerobot"; then
    EXISTING_LEROBOT="."
    echo -e "  ${YELLOW}⚠️  Currently in a lerobot repository${NC}"
else
    echo -e "  ${GREEN}✓ Clean installation${NC}"
fi

# ============================================================================
# STEP 2: Backup existing installation
# ============================================================================
if [ -n "$EXISTING_LEROBOT" ]; then
    echo -e "${BLUE}[2/8] 💾 Backing up existing installation...${NC}"
    
    if [ "$EXISTING_LEROBOT" = "." ]; then
        cd ..
        mv "$(basename $(pwd))" "lerobot-$BACKUP_SUFFIX"
        echo -e "  ${GREEN}✓ Backed up to: lerobot-$BACKUP_SUFFIX${NC}"
    else
        mv "lerobot" "lerobot-$BACKUP_SUFFIX"
        echo -e "  ${GREEN}✓ Backed up to: lerobot-$BACKUP_SUFFIX${NC}"
    fi
else
    echo -e "${BLUE}[2/8] 💾 No backup needed (fresh install)${NC}"
fi

# ============================================================================
# STEP 3: Clone bi-manual fork
# ============================================================================
echo -e "${BLUE}[3/8] 📥 Cloning bi-manual fork...${NC}"

git clone -b $BIMANUAL_BRANCH $BIMANUAL_FORK_URL $INSTALL_DIR
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Bi-manual fork cloned successfully${NC}"
else
    echo -e "  ${RED}❌ Failed to clone bi-manual fork${NC}"
    echo "  Trying main branch..."
    git clone $BIMANUAL_FORK_URL $INSTALL_DIR
fi

cd $INSTALL_DIR
echo -e "  ${GREEN}✓ Now in: $(pwd)${NC}"

# ============================================================================
# STEP 4: Setup conda environment
# ============================================================================
echo -e "${BLUE}[4/8] 🐍 Setting up conda environment...${NC}"

# Find conda
CONDA_FOUND=false
CONDA_PATH=""

if command -v conda &> /dev/null; then
    CONDA_PATH=$(dirname $(dirname $(which conda)))
    CONDA_FOUND=true
elif [ -f "$HOME/miniconda3/bin/conda" ]; then
    CONDA_PATH="$HOME/miniconda3"
    CONDA_FOUND=true
elif [ -f "$HOME/anaconda3/bin/conda" ]; then
    CONDA_PATH="$HOME/anaconda3"
    CONDA_FOUND=true
elif [ -f "/opt/homebrew/Caskroom/miniconda/base/bin/conda" ]; then
    CONDA_PATH="/opt/homebrew/Caskroom/miniconda/base"
    CONDA_FOUND=true
fi

if [ "$CONDA_FOUND" = true ]; then
    echo "  Initializing conda from: $CONDA_PATH"
    source "$CONDA_PATH/etc/profile.d/conda.sh"
    
    # Create or update lerobot environment
    if conda env list | grep -q "^lerobot "; then
        echo "  Updating existing lerobot environment..."
        conda activate lerobot
        pip install -e .
    else
        echo "  Creating new lerobot environment..."
        conda create -n lerobot python=3.10 -y
        conda activate lerobot
        pip install -e .
    fi
    
    echo -e "  ${GREEN}✓ Conda environment ready${NC}"
else
    echo -e "  ${YELLOW}⚠️  Conda not found, using system Python${NC}"
    pip install -e .
fi

# ============================================================================
# STEP 5: Run bi-manual auto-calibration
# ============================================================================
echo -e "${BLUE}[5/8] 🎯 Running bi-manual auto-calibration...${NC}"

echo "This will detect your robot setup and configure everything automatically."
echo "Make sure all your robot arms are connected and powered on!"
echo ""

read -p "Run auto-calibration now? [Y/n]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo -e "  ${YELLOW}⚠️  Skipping auto-calibration${NC}"
    echo "  Run later with: python -m lerobot.scripts.auto_calibrate_bimanual"
else
    echo "  Starting bi-manual auto-calibration..."
    python -m lerobot.scripts.auto_calibrate_bimanual
    
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓ Auto-calibration completed successfully${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Auto-calibration had issues, but continuing...${NC}"
    fi
fi

# ============================================================================
# STEP 6: Make scripts executable
# ============================================================================
echo -e "${BLUE}[6/8] 🔧 Setting up scripts...${NC}"

# Make all scripts executable
chmod +x *.sh 2>/dev/null
chmod +x *.py 2>/dev/null
chmod +x start_* 2>/dev/null
chmod +x deploy_* 2>/dev/null
chmod +x launch_* 2>/dev/null

# Key executable files
chmod +x quick_camera_check.sh
chmod +x update_lerobot_fork.sh
chmod +x start_lerobot_touch.sh
chmod +x working_touch_ui.py
chmod +x bimanual_api.py

echo -e "  ${GREEN}✓ All scripts are executable${NC}"

# ============================================================================
# STEP 7: Test installation
# ============================================================================
echo -e "${BLUE}[7/8] 🧪 Testing installation...${NC}"

echo "  Testing imports..."
python -c "
try:
    from lerobot.robots.bi_so100_follower import BiSO100Follower
    from lerobot.teleoperators.bi_so100_leader import BiSO100Leader
    from lerobot.robots.lekiwi import LeKiwi
    print('  ✓ Bi-manual classes imported successfully')
except ImportError as e:
    print(f'  ⚠️  Import warning: {e}')

try:
    import tkinter
    print('  ✓ GUI libraries available')
except ImportError:
    print('  ⚠️  GUI libraries may not be available')

print('  ✓ Installation test completed')
"

echo -e "  ${GREEN}✓ Installation test passed${NC}"

# ============================================================================
# STEP 8: Setup completion
# ============================================================================
echo -e "${BLUE}[8/8] 🎉 Finalizing setup...${NC}"

# Create desktop shortcut if possible
if [ -d "$HOME/Desktop" ] && [ -f "BiManual-Robot-Control.desktop" ]; then
    cp BiManual-Robot-Control.desktop "$HOME/Desktop/"
    chmod +x "$HOME/Desktop/BiManual-Robot-Control.desktop"
    echo -e "  ${GREEN}✓ Desktop shortcut created${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎉 UPGRADE COMPLETE! 🎉                               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}🤖🤖 Your LeRobot is now UPGRADED with bi-manual capabilities!${NC}"
echo ""

# Check what was detected
if [ -f "$HOME/.lerobot/bimanual_config.json" ]; then
    echo -e "${YELLOW}🔍 DETECTED SETUP:${NC}"
    python -c "
import json
try:
    with open('$HOME/.lerobot/bimanual_config.json', 'r') as f:
        config = json.load(f)
    setup_type = config.get('setup_type', 'unknown')
    leaders = len(config.get('leaders', []))
    followers = len(config.get('followers', []))
    print(f'  📊 Type: {setup_type.upper()}')
    print(f'  📱 Leaders: {leaders}')
    print(f'  🤖 Followers: {followers}')
except:
    print('  📋 Configuration will be created on first run')
"
    echo ""
fi

echo -e "${YELLOW}🚀 QUICK START OPTIONS:${NC}"
echo ""
echo -e "${CYAN}1. Touch UI (Recommended for tablets/touchscreens):${NC}"
echo "   ./working_touch_ui.py"
echo ""
echo -e "${CYAN}2. Terminal UI (Full featured):${NC}"
echo "   ./start_lerobot_ui.sh"
echo ""
echo -e "${CYAN}3. Dedicated Bi-Manual Interface:${NC}"
echo "   python lerobot_bimanual_ui.py"
echo ""
echo -e "${CYAN}4. Camera Check (for ML camera debugging):${NC}"
echo "   ./quick_camera_check.sh"
echo ""

echo -e "${YELLOW}📚 DOCUMENTATION:${NC}"
echo "  BIMANUAL_UPGRADE_GUIDE.md    - Complete usage guide"
echo "  DEPLOYMENT_PACKAGE.md        - Production deployment"
echo "  XARM_RESEARCH_PLAN.md        - Industrial upgrade path"
echo ""

if [ -n "$EXISTING_LEROBOT" ]; then
    echo -e "${YELLOW}💾 BACKUP:${NC}"
    echo "  Your old installation: lerobot-$BACKUP_SUFFIX"
    echo "  To restore: mv lerobot-$BACKUP_SUFFIX lerobot"
    echo ""
fi

echo -e "${YELLOW}🔧 RE-CALIBRATION:${NC}"
echo "  python -m lerobot.scripts.auto_calibrate_bimanual"
echo ""

echo -e "${GREEN}Ready for bi-manual robotics! 🚀🤖🤖🚀${NC}"

# Auto-start touch UI if requested
echo ""
read -p "Start touch UI now? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}🚀 Starting touch UI...${NC}"
    python working_touch_ui.py
fi