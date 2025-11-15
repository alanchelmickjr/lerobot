#!/bin/bash

# Deploy SO-101 Robot Control GUI to Remote System
# Target: 192.168.88.141 (feetech@192.168.88.141)

set -e

# Configuration
REMOTE_HOST="192.168.88.141"
REMOTE_USER="feetech"
REMOTE_PATH="/home/feetech/so101_control"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

print_color "🚀 SO-101 GUI Deployment Script" "$BLUE"
print_color "================================" "$BLUE"
print_color "Target: $REMOTE_USER@$REMOTE_HOST" "$GREEN"
print_color "Path: $REMOTE_PATH" "$GREEN"
echo ""

# Check if files exist
print_color "📦 Checking local files..." "$YELLOW"
REQUIRED_FILES=(
    "so101_robot_control_gui.py"
    "launch_so101_gui.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_color "  ✅ Found: $file" "$GREEN"
    else
        print_color "  ❌ Missing: $file" "$RED"
        exit 1
    fi
done

# Make launcher executable
chmod +x launch_so101_gui.sh

# Test SSH connection
print_color "\n🔌 Testing SSH connection..." "$YELLOW"
if ssh -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST "echo 'Connected'" > /dev/null 2>&1; then
    print_color "✅ SSH connection successful" "$GREEN"
else
    print_color "❌ Cannot connect to $REMOTE_USER@$REMOTE_HOST" "$RED"
    print_color "Please ensure:" "$YELLOW"
    print_color "  1. The remote system is powered on" "$YELLOW"
    print_color "  2. You're on the same network" "$YELLOW"
    print_color "  3. SSH is enabled on the remote system" "$YELLOW"
    exit 1
fi

# Create remote directory
print_color "\n📁 Creating remote directory..." "$YELLOW"
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_PATH"

# Copy files
print_color "\n📤 Copying files to remote system..." "$YELLOW"
for file in "${REQUIRED_FILES[@]}"; do
    print_color "  Copying: $file" "$BLUE"
    scp "$file" $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/
done

# Set permissions on remote
print_color "\n🔧 Setting remote permissions..." "$YELLOW"
ssh $REMOTE_USER@$REMOTE_HOST "chmod +x $REMOTE_PATH/launch_so101_gui.sh"

# Create desktop shortcut
print_color "\n🖥️ Creating desktop shortcut..." "$YELLOW"
cat > so101_control.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SO-101 Robot Control
Comment=Control SO-101 bimanual robots
Icon=applications-robotics
Exec=$REMOTE_PATH/launch_so101_gui.sh
Terminal=false
Categories=Development;Robotics;
StartupWMClass=so101_control
EOF

scp so101_control.desktop $REMOTE_USER@$REMOTE_HOST:~/Desktop/
ssh $REMOTE_USER@$REMOTE_HOST "chmod +x ~/Desktop/so101_control.desktop"
rm so101_control.desktop

# Install dependencies on remote
print_color "\n📦 Checking remote dependencies..." "$YELLOW"
ssh $REMOTE_USER@$REMOTE_HOST << 'REMOTE_SCRIPT'
set -e

# Function to print colored output
print_remote() {
    echo -e "\033[0;33m  Remote: $1\033[0m"
}

# Check Python
if command -v python3 &> /dev/null; then
    print_remote "✅ Python3 found: $(python3 --version)"
else
    print_remote "⚠️ Python3 not found, installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-tk
fi

# Check tkinter
if python3 -c "import tkinter" 2>/dev/null; then
    print_remote "✅ Tkinter is installed"
else
    print_remote "⚠️ Installing tkinter..."
    sudo apt-get install -y python3-tk
fi

# Check pyserial
if python3 -c "import serial" 2>/dev/null; then
    print_remote "✅ PySerial is installed"
else
    print_remote "⚠️ Installing pyserial..."
    pip3 install pyserial
fi

print_remote "✅ All dependencies checked"
REMOTE_SCRIPT

# Create autostart entry for kiosk mode
print_color "\n🚀 Setting up autostart..." "$YELLOW"
ssh $REMOTE_USER@$REMOTE_HOST << AUTOSTART
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/so101_control.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=SO-101 Robot Control
Exec=$REMOTE_PATH/launch_so101_gui.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Start SO-101 Robot Control on login
EOF
AUTOSTART

print_color "\n✅ Deployment complete!" "$GREEN"
print_color "================================" "$BLUE"
print_color "\nThe SO-101 Robot Control GUI has been deployed to:" "$GREEN"
print_color "  Host: $REMOTE_USER@$REMOTE_HOST" "$GREEN"
print_color "  Path: $REMOTE_PATH" "$GREEN"
print_color "\nFeatures installed:" "$GREEN"
print_color "  ✅ GUI application" "$GREEN"
print_color "  ✅ Launcher script" "$GREEN"
print_color "  ✅ Desktop shortcut" "$GREEN"
print_color "  ✅ Autostart on login" "$GREEN"
print_color "\nTo run on the remote system:" "$YELLOW"
print_color "  1. SSH: ssh $REMOTE_USER@$REMOTE_HOST" "$YELLOW"
print_color "  2. Run: $REMOTE_PATH/launch_so101_gui.sh" "$YELLOW"
print_color "\nOr double-click the desktop shortcut on the remote system!" "$YELLOW"