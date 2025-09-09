#!/bin/bash

# Script to completely remove all conda installations
set -e

echo "=================================================="
echo "🧹 Complete Conda Cleanup Script"
echo "=================================================="
echo ""
echo "This script will remove ALL conda installations including:"
echo "  • Homebrew conda/miniconda/anaconda"
echo "  • Local miniconda3/anaconda3 installations"
echo "  • Conda configuration files"
echo ""
read -p "Are you sure you want to continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "📦 Step 1: Removing Homebrew conda packages..."
# Remove conda/miniconda/anaconda from Homebrew if installed
brew uninstall --ignore-dependencies miniconda 2>/dev/null || echo "  ✓ miniconda not found in brew"
brew uninstall --ignore-dependencies anaconda 2>/dev/null || echo "  ✓ anaconda not found in brew"
brew uninstall --ignore-dependencies conda 2>/dev/null || echo "  ✓ conda not found in brew"

echo ""
echo "🗑️ Step 2: Removing local conda installations..."
# Remove local installations
rm -rf ~/miniconda3 2>/dev/null && echo "  ✓ Removed ~/miniconda3" || echo "  ✓ ~/miniconda3 not found"
rm -rf ~/anaconda3 2>/dev/null && echo "  ✓ Removed ~/anaconda3" || echo "  ✓ ~/anaconda3 not found"
rm -rf ~/miniforge3 2>/dev/null && echo "  ✓ Removed ~/miniforge3" || echo "  ✓ ~/miniforge3 not found"
rm -rf /opt/miniconda3 2>/dev/null && echo "  ✓ Removed /opt/miniconda3" || echo "  ✓ /opt/miniconda3 not found"
rm -rf /opt/anaconda3 2>/dev/null && echo "  ✓ Removed /opt/anaconda3" || echo "  ✓ /opt/anaconda3 not found"

echo ""
echo "🔧 Step 3: Removing conda configuration files..."
# Remove configuration files
rm -rf ~/.conda 2>/dev/null && echo "  ✓ Removed ~/.conda" || echo "  ✓ ~/.conda not found"
rm -f ~/.condarc 2>/dev/null && echo "  ✓ Removed ~/.condarc" || echo "  ✓ ~/.condarc not found"
rm -rf ~/.config/conda 2>/dev/null && echo "  ✓ Removed ~/.config/conda" || echo "  ✓ ~/.config/conda not found"

echo ""
echo "📝 Step 4: Cleaning shell configuration files..."
# Clean .zshrc
if [ -f ~/.zshrc ]; then
    cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
    echo "  ✓ Created backup: ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Remove conda initialization block
    sed -i '' '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' ~/.zshrc
    echo "  ✓ Removed conda initialization from ~/.zshrc"
fi

# Clean .bashrc
if [ -f ~/.bashrc ]; then
    cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)
    echo "  ✓ Created backup: ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Remove conda initialization block
    sed -i '' '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' ~/.bashrc
    echo "  ✓ Removed conda initialization from ~/.bashrc"
fi

# Clean .bash_profile
if [ -f ~/.bash_profile ]; then
    cp ~/.bash_profile ~/.bash_profile.backup.$(date +%Y%m%d_%H%M%S)
    echo "  ✓ Created backup: ~/.bash_profile.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Remove conda initialization block
    sed -i '' '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' ~/.bash_profile
    echo "  ✓ Removed conda initialization from ~/.bash_profile"
fi

echo ""
echo "=================================================="
echo "✅ Cleanup Complete!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. RESTART YOUR COMPUTER to ensure all changes take effect"
echo ""
echo "2. After restart, install Miniconda fresh from:"
echo "   https://docs.conda.io/en/latest/miniconda.html"
echo ""
echo "   For macOS Apple Silicon (M1/M2/M3):"
echo "   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
echo "   bash Miniconda3-latest-MacOSX-arm64.sh"
echo ""
echo "   For macOS Intel:"
echo "   curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
echo "   bash Miniconda3-latest-MacOSX-x86_64.sh"
echo ""
echo "3. After installation, create LeRobot environment:"
echo "   conda create -n lerobot python=3.10"
echo "   conda activate lerobot"
echo "   conda install ffmpeg -c conda-forge"
echo "   pip install -e '.[feetech]'"
echo ""
echo "=================================================="