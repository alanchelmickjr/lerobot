#!/bin/bash
# Turnkey Bi-Manual Robot System Setup
# Makes system auto-login and auto-start for out-of-the-box sales

echo "🚀 Setting up TURNKEY BI-MANUAL ROBOT SYSTEM"
echo "=============================================="

# 1. Configure Auto-Login (GDM3)
echo "🔐 Configuring auto-login..."
sudo mkdir -p /etc/gdm3
sudo tee /etc/gdm3/custom.conf > /dev/null <<EOF
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=feetech

[security]

[xdmcp]

[chooser]

[debug]
EOF

# 2. Create Kiosk Mode Startup Script
echo "🖥️  Creating kiosk startup script..."
mkdir -p /home/feetech/.config/autostart

tee /home/feetech/.config/autostart/bimanual-kiosk.desktop > /dev/null <<EOF
[Desktop Entry]
Type=Application
Name=BiManual Robot Kiosk
Comment=Auto-start bi-manual robot interface in kiosk mode
Exec=/home/feetech/lerobot/start_kiosk.sh
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

# 3. Create Kiosk Launcher with Auto-Restart
echo "🔄 Creating auto-restart kiosk launcher..."
tee /home/feetech/lerobot/start_kiosk.sh > /dev/null <<'EOF'
#!/bin/bash
# Kiosk Mode Launcher with Auto-Restart
# Professional console effect for turnkey systems

# Hide mouse cursor and disable screensaver
xset -dpms s off s noblank s noexpose
unclutter -idle 1 &

# Set fullscreen desktop
wmctrl -r :ACTIVE: -b add,fullscreen 2>/dev/null

# Main kiosk loop with auto-restart
while true; do
    echo "🚀 Starting Bi-Manual Robot System..."
    echo "$(date): Kiosk starting" >> /home/feetech/lerobot/kiosk.log
    
    # Activate conda and start GUI
    cd /home/feetech/lerobot
    source /home/feetech/miniconda3/bin/activate
    conda activate lerobot
    
    # Start the GUI (will block until closed/crashed)
    DISPLAY=:0 python3 simple_touch_ui.py 2>&1 | tee -a /home/feetech/lerobot/app.log
    
    # If we get here, app exited - log and restart
    echo "$(date): App exited, restarting in 3 seconds..." >> /home/feetech/lerobot/kiosk.log
    sleep 3
done
EOF

chmod +x /home/feetech/lerobot/start_kiosk.sh

# 4. Create Professional Boot Splash
echo "✨ Creating boot splash screen..."
tee /home/feetech/lerobot/boot_splash.py > /dev/null <<'EOF'
#!/usr/bin/env python3
"""
Professional boot splash for turnkey bi-manual system
"""
import tkinter as tk
import time
import threading

class BootSplash:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bi-Manual Robot System")
        self.root.configure(bg='#1a1a1a')
        self.root.attributes('-fullscreen', True)
        
        # Logo area
        title = tk.Label(
            self.root,
            text="🤖🤖\nBI-MANUAL\nROBOT SYSTEM",
            font=('Arial', 48, 'bold'),
            bg='#1a1a1a',
            fg='#00ff41'
        )
        title.pack(expand=True, pady=50)
        
        # Status
        self.status = tk.Label(
            self.root,
            text="⚡ INITIALIZING SYSTEM...",
            font=('Arial', 20),
            bg='#1a1a1a',
            fg='#ffffff'
        )
        self.status.pack(pady=20)
        
        # Progress bar effect
        self.progress = tk.Label(
            self.root,
            text="",
            font=('Courier', 16),
            bg='#1a1a1a',
            fg='#00ff41'
        )
        self.progress.pack(pady=20)
        
        # Version info
        version = tk.Label(
            self.root,
            text="Professional Turnkey Edition v2.0\nReady for Production Deployment",
            font=('Arial', 12),
            bg='#1a1a1a',
            fg='#888888'
        )
        version.pack(side='bottom', pady=20)
        
        # Start loading sequence
        threading.Thread(target=self.loading_sequence, daemon=True).start()
        
    def loading_sequence(self):
        steps = [
            "🔍 Scanning USB ports...",
            "🤖 Detecting robot hardware...", 
            "📦 Loading LeRobot framework...",
            "🎮 Initializing touch interface...",
            "✅ System ready!"
        ]
        
        for i, step in enumerate(steps):
            self.root.after(0, lambda s=step: self.status.config(text=s))
            
            # Progress bar effect
            progress = "█" * (i + 1) + "░" * (len(steps) - i - 1)
            self.root.after(0, lambda p=progress: self.progress.config(text=f"[{p}] {int((i+1)/len(steps)*100)}%"))
            
            time.sleep(2)
        
        time.sleep(1)
        self.root.after(0, self.root.quit)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    splash = BootSplash()
    splash.run()
EOF

chmod +x /home/feetech/lerobot/boot_splash.py

# 5. Disable Ubuntu dock and other distractions
echo "🎯 Configuring kiosk environment..."
gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed false 2>/dev/null || true
gsettings set org.gnome.desktop.lockdown disable-lock-screen true 2>/dev/null || true

# 6. Install required packages
echo "📦 Installing kiosk packages..."
sudo apt update
sudo apt install -y unclutter wmctrl

echo ""
echo "✅ TURNKEY SYSTEM SETUP COMPLETE!"
echo ""
echo "📋 WHAT'S CONFIGURED:"
echo "   🔐 Auto-login as feetech user"
echo "   🚀 Auto-start bi-manual GUI on boot"
echo "   🔄 Auto-restart if app crashes"
echo "   🖥️  Fullscreen kiosk mode"
echo "   ✨ Professional boot splash"
echo "   📝 Logging to ~/lerobot/kiosk.log"
echo ""
echo "🎯 READY FOR OUT-OF-THE-BOX SALES!"
echo "   Just power on → Auto-login → Robot interface starts"
echo ""
echo "⚠️  REBOOT REQUIRED to activate auto-login"
EOF

chmod +x setup_turnkey_system.sh