#!/bin/bash

# ============================================================================
# 🚀 Deploy Bi-Manual System to Coofun Mini-PC
# ============================================================================
# SSH deployment with auto-startup daemon setup
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Coofun connection details
COOFUN_IP="192.168.88.22"
COOFUN_USER="feetech"
COOFUN_PASS="feetech"
REMOTE_DIR="/home/feetech/lerobot"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              🚀 Coofun Mini-PC Deployment Script 🚀                 ║"
echo "║                   Bi-Manual System + Auto-Daemon                     ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Check if sshpass is available (for password automation)
# ============================================================================
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}⚠️  sshpass not found. Install it for automated deployment:${NC}"
    echo "  macOS: brew install sshpass"
    echo "  Ubuntu: sudo apt-get install sshpass"
    echo ""
    echo -e "${BLUE}Using manual SSH instead...${NC}"
    USE_SSHPASS=false
else
    echo -e "${GREEN}✓ sshpass found - using automated deployment${NC}"
    USE_SSHPASS=true
fi

# ============================================================================
# Function to run SSH commands
# ============================================================================
ssh_cmd() {
    if [ "$USE_SSHPASS" = true ]; then
        sshpass -p "$COOFUN_PASS" ssh -o StrictHostKeyChecking=no "$COOFUN_USER@$COOFUN_IP" "$1"
    else
        echo -e "${YELLOW}Run this command on Coofun (password: $COOFUN_PASS):${NC}"
        echo "  $1"
        read -p "Press Enter when done..."
    fi
}

# Function to copy files
scp_file() {
    local file="$1"
    local dest="$2"
    
    if [ "$USE_SSHPASS" = true ]; then
        sshpass -p "$COOFUN_PASS" scp -o StrictHostKeyChecking=no "$file" "$COOFUN_USER@$COOFUN_IP:$dest"
    else
        echo -e "${YELLOW}Copy this file to Coofun:${NC}"
        echo "  Local: $file"
        echo "  Remote: $COOFUN_USER@$COOFUN_IP:$dest"
        read -p "Press Enter when copied..."
    fi
}

# ============================================================================
# Step 1: Test connection
# ============================================================================
echo -e "${BLUE}[1/6] 🔗 Testing connection to Coofun...${NC}"

if [ "$USE_SSHPASS" = true ]; then
    if sshpass -p "$COOFUN_PASS" ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$COOFUN_USER@$COOFUN_IP" "echo 'Connection successful'"; then
        echo -e "  ${GREEN}✓ Connected to Coofun Mini-PC${NC}"
    else
        echo -e "  ${RED}❌ Connection failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Please test SSH connection manually:${NC}"
    echo "  ssh $COOFUN_USER@$COOFUN_IP"
    read -p "Press Enter if connection works, Ctrl+C if not..."
fi

# ============================================================================
# Step 2: Create directory structure
# ============================================================================
echo -e "${BLUE}[2/6] 📁 Setting up directories...${NC}"

ssh_cmd "mkdir -p $REMOTE_DIR"
ssh_cmd "mkdir -p $REMOTE_DIR/scripts"
ssh_cmd "mkdir -p ~/.config/systemd/user"

# ============================================================================
# Step 3: Copy bi-manual files
# ============================================================================
echo -e "${BLUE}[3/6] 📦 Copying bi-manual system files...${NC}"

# Core files
scp_file "lerobot_touch_ui.py" "$REMOTE_DIR/"
scp_file "lerobot_teleop_ui.py" "$REMOTE_DIR/"
scp_file "test_bimanual_setup.py" "$REMOTE_DIR/"
scp_file "start_lerobot_touch.sh" "$REMOTE_DIR/"
scp_file "update_lerobot_fork.sh" "$REMOTE_DIR/"

# Documentation
scp_file "BIMANUAL_UPGRADE_GUIDE.md" "$REMOTE_DIR/"
scp_file "DEPLOYMENT_PACKAGE.md" "$REMOTE_DIR/"

echo -e "  ${GREEN}✓ Core files copied${NC}"

# ============================================================================
# Step 4: Create auto-detection daemon script
# ============================================================================
echo -e "${BLUE}[4/6] 🤖 Creating auto-detection daemon...${NC}"

cat > bimanual_daemon.py << 'EOF'
#!/usr/bin/env python3
"""
🤖 Bi-Manual Auto-Detection Daemon
Monitors USB ports and auto-launches touch UI when 4 SO101 arms detected
"""

import time
import subprocess
import sys
import os
import logging
import signal
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BiManualDaemon - %(message)s',
    handlers=[
        logging.FileHandler('/home/feetech/bimanual_daemon.log'),
        logging.StreamHandler()
    ]
)

class BiManualDaemon:
    def __init__(self):
        self.running = True
        self.ui_process = None
        self.last_check = 0
        self.check_interval = 5  # Check every 5 seconds
        
    def find_usb_ports(self) -> List[str]:
        """Find USB serial ports"""
        import serial.tools.list_ports
        ports = []
        
        for port in serial.tools.list_ports.comports():
            device_lower = port.device.lower()
            if any(pattern in device_lower for pattern in ['usb', 'usbmodem', 'usbserial', 'acm']):
                ports.append(port.device)
        
        return sorted(ports)
    
    def detect_bimanual_setup(self) -> Optional[Dict]:
        """Quick bi-manual detection"""
        try:
            from lerobot.motors.feetech import FeetechMotorsBus
            
            ports = self.find_usb_ports()
            if len(ports) != 4:
                return None
                
            leaders = []
            followers = []
            
            for port in ports:
                try:
                    bus = FeetechMotorsBus(port=port, motors={})
                    bus.connect()
                    found_ids = bus.scan()
                    
                    if found_ids:
                        voltage = bus.read("Present_Voltage", found_ids[0]) / 10.0
                        if voltage < 8.0:
                            leaders.append(port)
                        elif voltage > 10.0:
                            followers.append(port)
                    bus.disconnect()
                except Exception:
                    pass
            
            if len(leaders) == 2 and len(followers) == 2:
                return {
                    "left_leader": leaders[0], "left_follower": followers[0],
                    "right_leader": leaders[1], "right_follower": followers[1]
                }
        except Exception as e:
            logging.warning(f"Detection error: {e}")
        
        return None
    
    def launch_touch_ui(self):
        """Launch the touch UI"""
        if self.ui_process and self.ui_process.poll() is None:
            logging.info("Touch UI already running")
            return
        
        try:
            # Set display for X11
            env = os.environ.copy()
            env['DISPLAY'] = ':0'
            
            # Launch touch UI
            cmd = ['/home/feetech/lerobot/start_lerobot_touch.sh']
            
            self.ui_process = subprocess.Popen(
                cmd,
                env=env,
                cwd='/home/feetech/lerobot',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            logging.info(f"Touch UI launched (PID: {self.ui_process.pid})")
            
        except Exception as e:
            logging.error(f"Failed to launch UI: {e}")
    
    def stop_touch_ui(self):
        """Stop the touch UI"""
        if self.ui_process and self.ui_process.poll() is None:
            self.ui_process.terminate()
            time.sleep(2)
            if self.ui_process.poll() is None:
                self.ui_process.kill()
            logging.info("Touch UI stopped")
    
    def run(self):
        """Main daemon loop"""
        logging.info("Bi-Manual Daemon started")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check every interval
                if current_time - self.last_check >= self.check_interval:
                    self.last_check = current_time
                    
                    # Check for bi-manual setup
                    bimanual_config = self.detect_bimanual_setup()
                    
                    if bimanual_config:
                        logging.info("Bi-manual setup detected - launching UI")
                        self.launch_touch_ui()
                    else:
                        # No bi-manual setup - stop UI if running
                        if self.ui_process and self.ui_process.poll() is None:
                            logging.info("Bi-manual setup lost - stopping UI")
                            self.stop_touch_ui()
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Daemon error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop daemon"""
        self.running = False
        self.stop_touch_ui()
        logging.info("Daemon stopping")

# Signal handlers
daemon = BiManualDaemon()

def signal_handler(signum, frame):
    daemon.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    daemon.run()
EOF

scp_file "bimanual_daemon.py" "$REMOTE_DIR/"

# ============================================================================
# Step 5: Create systemd service
# ============================================================================
echo -e "${BLUE}[5/6] ⚙️ Setting up systemd service...${NC}"

cat > bimanual-daemon.service << 'EOF'
[Unit]
Description=LeRobot Bi-Manual Auto-Detection Daemon
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=feetech
Group=feetech
Environment=DISPLAY=:0
Environment=PYTHONPATH=/home/feetech/lerobot
WorkingDirectory=/home/feetech/lerobot
ExecStart=/home/feetech/miniconda3/envs/lerobot/bin/python /home/feetech/lerobot/bimanual_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

scp_file "bimanual-daemon.service" "~/.config/systemd/user/"

# ============================================================================
# Step 6: Enable and start daemon
# ============================================================================
echo -e "${BLUE}[6/6] 🚀 Enabling auto-startup daemon...${NC}"

# Make scripts executable
ssh_cmd "chmod +x $REMOTE_DIR/*.sh $REMOTE_DIR/*.py"

# Enable systemd user service
ssh_cmd "systemctl --user daemon-reload"
ssh_cmd "systemctl --user enable bimanual-daemon.service"
ssh_cmd "systemctl --user start bimanual-daemon.service"

# Enable user services at boot
ssh_cmd "sudo loginctl enable-linger feetech"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                     🎉 DEPLOYMENT COMPLETE! 🎉                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}What's deployed:${NC}"
echo "  🤖 Bi-manual touch UI optimized for 7\" screen"
echo "  🔍 Auto-detection daemon (monitors USB ports)"
echo "  ⚙️  Systemd service (auto-starts at boot)"
echo "  📁 All files in $REMOTE_DIR"
echo ""
echo -e "${YELLOW}How it works:${NC}"
echo "  1. Daemon monitors USB ports every 5 seconds"
echo "  2. When 4 SO101 arms detected → Auto-launches touch UI"
echo "  3. When arms disconnected → Auto-stops UI"
echo "  4. Starts automatically on boot"
echo ""
echo -e "${YELLOW}Manual controls:${NC}"
echo "  Check daemon status: systemctl --user status bimanual-daemon"
echo "  Stop daemon: systemctl --user stop bimanual-daemon"
echo "  View logs: journalctl --user -u bimanual-daemon -f"
echo ""
echo -e "${GREEN}Ready! Connect your 4 SO101 arms and watch the magic! ✨🤖🤖${NC}"

# Clean up temp files
rm -f bimanual_daemon.py bimanual-daemon.service

echo -e "${CYAN}Deployment script complete!${NC}"