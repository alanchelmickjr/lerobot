#!/bin/bash

# ============================================================================
# 🚀 LeRobot Fork Update Script - One command to rule them all!
# ============================================================================
# Usage: 
#   curl -sSL https://raw.githubusercontent.com/YOUR-FORK/lerobot/main/update_lerobot_fork.sh | bash
#   OR
#   ./update_lerobot_fork.sh
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                🚀 LeRobot Fork Update System 🚀                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
YOUR_FORK_URL="https://github.com/YOUR-USERNAME/lerobot.git"
YOUR_BRANCH="bimanual-improvements"  # Change this to your branch name
BACKUP_BRANCH="backup-$(date +%Y%m%d-%H%M%S)"

# ============================================================================
# STEP 1: Check if we're in a lerobot directory
# ============================================================================
echo -e "${BLUE}[1/6] 🔍 Checking environment...${NC}"

if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not in a git repository!${NC}"
    echo "Please run this from your lerobot directory, or clone first:"
    echo "  git clone https://github.com/huggingface/lerobot.git"
    echo "  cd lerobot"
    echo "  ./update_lerobot_fork.sh"
    exit 1
fi

# Check if we're in lerobot repo
if ! git remote -v | grep -q "lerobot"; then
    echo -e "${YELLOW}⚠️  This doesn't look like a lerobot repository${NC}"
    echo "Continuing anyway..."
fi

echo -e "  ${GREEN}✓ Git repository detected${NC}"

# ============================================================================
# STEP 2: Backup current state
# ============================================================================
echo -e "${BLUE}[2/6] 💾 Creating backup...${NC}"

# Create backup branch
git branch $BACKUP_BRANCH 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Backup branch created: $BACKUP_BRANCH${NC}"
else
    echo -e "  ${YELLOW}⚠️  Backup branch already exists${NC}"
fi

# ============================================================================
# STEP 3: Add your fork as remote
# ============================================================================
echo -e "${BLUE}[3/6] 🔗 Setting up fork remote...${NC}"

# Check if fork remote exists
if git remote | grep -q "fork"; then
    echo -e "  ${YELLOW}⚠️  Fork remote already exists, updating URL...${NC}"
    git remote set-url fork $YOUR_FORK_URL
else
    echo -e "  ${GREEN}✓ Adding fork remote...${NC}"
    git remote add fork $YOUR_FORK_URL
fi

# ============================================================================
# STEP 4: Fetch latest changes
# ============================================================================
echo -e "${BLUE}[4/6] 📡 Fetching latest changes...${NC}"

echo "  Fetching from original repo..."
git fetch origin

echo "  Fetching from your fork..."
git fetch fork

echo -e "  ${GREEN}✓ Fetch complete${NC}"

# ============================================================================
# STEP 5: Switch to your improved branch
# ============================================================================
echo -e "${BLUE}[5/6] 🔄 Switching to improvements branch...${NC}"

# Check if local branch exists
if git branch | grep -q $YOUR_BRANCH; then
    echo "  Switching to existing local branch..."
    git checkout $YOUR_BRANCH
    echo "  Pulling latest changes..."
    git pull fork $YOUR_BRANCH
else
    echo "  Creating new branch from fork..."
    git checkout -b $YOUR_BRANCH fork/$YOUR_BRANCH
fi

echo -e "  ${GREEN}✓ Now on branch: $YOUR_BRANCH${NC}"

# ============================================================================
# STEP 6: Update conda environment
# ============================================================================
echo -e "${BLUE}[6/6] 🐍 Updating conda environment...${NC}"

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
fi

if [ "$CONDA_FOUND" = true ]; then
    echo "  Initializing conda..."
    source "$CONDA_PATH/etc/profile.d/conda.sh"
    
    if conda env list | grep -q "^lerobot "; then
        echo "  Updating lerobot environment..."
        conda activate lerobot
        
        # Install in development mode with your improvements
        pip install -e .
        
        echo -e "  ${GREEN}✓ Environment updated${NC}"
    else
        echo -e "  ${YELLOW}⚠️  lerobot environment not found${NC}"
        echo "  Run: conda create -n lerobot python=3.10"
    fi
else
    echo -e "  ${YELLOW}⚠️  Conda not found, skipping environment update${NC}"
fi

# ============================================================================
# SUCCESS!
# ============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎉 UPDATE COMPLETE! 🎉                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Your LeRobot fork has been updated with latest improvements!${NC}"
echo ""
echo -e "${YELLOW}What's new:${NC}"
echo "  🤖🤖 Bi-manual SO101 support with mode selection"
echo "  🎮 Interactive coordination modes (Joint/Independent/Mirror)"
echo "  🔍 Auto-detection for 4-port setups"
echo "  📱 Enhanced UI with better port management"
echo ""
echo -e "${YELLOW}To get started:${NC}"
echo "  ./start_lerobot_ui.sh"
echo ""
echo -e "${YELLOW}Backup available at branch:${NC} $BACKUP_BRANCH"
echo -e "${YELLOW}To rollback:${NC} git checkout $BACKUP_BRANCH"
echo ""

# Make scripts executable
chmod +x start_lerobot_ui.sh 2>/dev/null
chmod +x lerobot_teleop_ui.py 2>/dev/null
chmod +x lerobot_bimanual_ui.py 2>/dev/null

echo -e "${GREEN}Ready to control your robots! 🚀${NC}"