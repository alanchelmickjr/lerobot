#!/bin/bash

# Script to install Miniconda3 and set up LeRobot environment
set -e

echo "=================================================="
echo "🚀 Installing Miniconda3 and Setting up LeRobot"
echo "=================================================="

# Detect system architecture and OS
ARCH=$(uname -m)
OS=$(uname -s)

echo "🔍 Detecting system..."
echo "   OS: $OS"
echo "   Architecture: $ARCH"

# Set the appropriate Miniconda URL based on OS and architecture
if [ "$OS" = "Darwin" ]; then
    # macOS
    if [ "$ARCH" = "arm64" ]; then
        # Apple Silicon (M1/M2/M3)
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
        echo "✅ Detected Apple Silicon Mac (arm64)"
    else
        # Intel Mac
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
        echo "✅ Detected Intel Mac (x86_64)"
    fi
elif [ "$OS" = "Linux" ]; then
    # Linux
    if [ "$ARCH" = "x86_64" ]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        echo "✅ Detected Linux x86_64"
    elif [ "$ARCH" = "aarch64" ]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
        echo "✅ Detected Linux ARM64/aarch64"
    else
        echo "❌ Unsupported Linux architecture: $ARCH"
        exit 1
    fi
else
    echo "❌ Unsupported operating system: $OS"
    echo "   This script supports macOS and Linux only."
    exit 1
fi

# Download Miniconda installer
echo ""
echo "📥 Downloading Miniconda3..."
curl -o ~/miniconda3_installer.sh $MINICONDA_URL

# Make installer executable
chmod +x ~/miniconda3_installer.sh

# Install Miniconda
echo ""
echo "📦 Installing Miniconda3..."
bash ~/miniconda3_installer.sh -b -p ~/miniconda3

# Remove installer
rm ~/miniconda3_installer.sh

# Initialize conda for the current shell
echo ""
echo "🔧 Initializing conda..."

# Detect and initialize for the current shell
if [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
    ~/miniconda3/bin/conda init zsh
    [ -f ~/.zshrc ] && source ~/.zshrc
elif [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
    ~/miniconda3/bin/conda init bash
    [ -f ~/.bashrc ] && source ~/.bashrc
else
    # Initialize both as fallback
    ~/miniconda3/bin/conda init bash
    ~/miniconda3/bin/conda init zsh
    [ -f ~/.bashrc ] && source ~/.bashrc
    [ -f ~/.zshrc ] && source ~/.zshrc
fi

# Add conda to PATH for this session
export PATH="$HOME/miniconda3/bin:$PATH"

echo ""
echo "✅ Miniconda3 installed successfully!"
echo ""
echo "=================================================="
echo "🤖 Setting up LeRobot Environment"
echo "=================================================="

# Create lerobot environment
echo ""
echo "📦 Creating lerobot conda environment with Python 3.10..."
~/miniconda3/bin/conda create -y -n lerobot python=3.10

# Activate the environment
echo ""
echo "🔄 Activating lerobot environment..."
source ~/miniconda3/bin/activate lerobot

# Install ffmpeg
echo ""
echo "📹 Installing ffmpeg..."
~/miniconda3/bin/conda install -n lerobot ffmpeg -c conda-forge -y

# Install LeRobot with feetech support for SO101
echo ""
echo "🤖 Installing LeRobot with feetech support..."
~/miniconda3/envs/lerobot/bin/pip install -e ".[feetech]"

# Install pyserial for USB communication
echo ""
echo "📡 Installing pyserial for USB communication..."
~/miniconda3/envs/lerobot/bin/pip install pyserial

# Platform-specific instructions
echo ""
echo "=================================================="
echo "✅ Installation Complete!"
echo "=================================================="
echo ""

if [ "$OS" = "Linux" ]; then
    echo "🐧 Linux-specific setup:"
    echo ""
    echo "For USB device access, you may need to:"
    echo "1. Add yourself to the dialout group:"
    echo "   sudo usermod -a -G dialout $USER"
    echo "2. Logout and login again for group changes to take effect"
    echo ""
    echo "Or for immediate access (temporary):"
    echo "   sudo chmod 666 /dev/ttyUSB*"
    echo ""
fi

echo "📝 Next Steps:"
echo ""
echo "1. Close and reopen your terminal for conda to be available"
echo "2. Activate the environment: conda activate lerobot"
echo "3. Run the auto-calibration: python -m lerobot.scripts.auto_calibrate_so101"
echo ""
echo "Or run this command to activate conda immediately:"
echo "   source ~/miniconda3/bin/activate"
echo "   conda activate lerobot"
echo ""
echo "=================================================="