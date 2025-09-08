#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Intelligent SO101 Auto-Calibration Script

This script automatically:
1. Detects which USB port is the leader vs follower arm
2. Handles USB permissions on macOS/Linux
3. Calibrates the follower arm with safety monitoring
4. Saves calibration for future use

Usage:
    python -m lerobot.scripts.auto_calibrate_so101
"""

import logging
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import serial.tools.list_ports

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SO101AutoCalibrator:
    """Automatic calibration system for SO101 arms."""
    
    def __init__(self):
        self.system = platform.system()
        self.leader_port: Optional[str] = None
        self.follower_port: Optional[str] = None
        
    def check_permissions(self) -> bool:
        """Check and fix USB permissions."""
        if self.system == "Linux":
            # Check if user is in dialout group
            try:
                groups = subprocess.check_output(['groups'], text=True)
                if 'dialout' not in groups:
                    logger.warning("User not in dialout group!")
                    self._fix_linux_permissions()
                    return False
            except Exception as e:
                logger.error(f"Error checking permissions: {e}")
                return False
                
        elif self.system == "Darwin":  # macOS
            # Check for USB device access
            try:
                # Test if we can list USB devices
                ports = list(serial.tools.list_ports.comports())
                if not ports:
                    logger.warning("No USB devices found or permission denied")
                    self._fix_macos_permissions()
                    return False
            except Exception as e:
                logger.error(f"Error accessing USB devices: {e}")
                self._fix_macos_permissions()
                return False
                
        return True
    
    def _fix_linux_permissions(self):
        """Fix Linux USB permissions."""
        print("\n" + "="*60)
        print("🔧 FIXING LINUX USB PERMISSIONS")
        print("="*60)
        print("\nTo access USB devices, you need to be in the 'dialout' group.")
        print("Run these commands:")
        print(f"\n  sudo usermod -a -G dialout {os.getlogin()}")
        print("  sudo chmod 666 /dev/ttyUSB*  # Temporary fix")
        print("\nThen logout and login again for permanent fix.")
        print("="*60)
        
        response = input("\nWould you like me to run the temporary fix now? (y/n): ")
        if response.lower() == 'y':
            try:
                subprocess.run(['sudo', 'chmod', '666'] + 
                             [f"/dev/ttyUSB{i}" for i in range(10)], 
                             capture_output=True)
                print("✅ Temporary permissions fixed! You can continue.")
            except Exception as e:
                print(f"❌ Failed to fix permissions: {e}")
    
    def _fix_macos_permissions(self):
        """Fix macOS USB permissions."""
        print("\n" + "="*60)
        print("🔧 FIXING MACOS USB PERMISSIONS")
        print("="*60)
        print("\nOn macOS, you may need to:")
        print("1. Install the FTDI driver: https://ftdichip.com/drivers/vcp-drivers/")
        print("2. Allow the driver in System Preferences > Security & Privacy")
        print("3. Grant Terminal/VS Code access to USB devices")
        print("\nIf using VS Code, also grant it access in:")
        print("  System Preferences > Security & Privacy > Privacy > Files and Folders")
        print("="*60)
        input("\nPress ENTER after completing these steps...")
    
    def list_usb_ports(self) -> list[str]:
        """List all available USB serial ports."""
        ports = []
        for port in serial.tools.list_ports.comports():
            # Filter for likely SO101 ports
            if self.system == "Darwin":  # macOS
                if "usbmodem" in port.device:
                    ports.append(port.device)
            elif self.system == "Linux":
                if "ttyUSB" in port.device or "ttyACM" in port.device:
                    ports.append(port.device)
            else:  # Windows
                if "COM" in port.device:
                    ports.append(port.device)
        return sorted(ports)
    
    def detect_arms(self) -> Tuple[Optional[str], Optional[str]]:
        """Intelligently detect which port is leader vs follower."""
        print("\n" + "="*60)
        print("🔍 INTELLIGENT ARM DETECTION")
        print("="*60)
        
        # Step 1: List all current ports
        initial_ports = self.list_usb_ports()
        
        if len(initial_ports) == 0:
            print("❌ No USB devices found! Please connect both arms.")
            return None, None
        elif len(initial_ports) == 1:
            print("⚠️  Only one USB device found. Please connect both arms.")
            return None, None
        elif len(initial_ports) > 2:
            print(f"⚠️  Found {len(initial_ports)} USB devices:")
            for i, port in enumerate(initial_ports):
                print(f"  {i+1}. {port}")
            print("\nWe'll identify your SO101 arms among these.")
        
        print(f"\n✅ Found {len(initial_ports)} USB devices:")
        for port in initial_ports:
            print(f"  • {port}")
        
        # Step 2: Identify LEADER arm
        print("\n" + "-"*40)
        print("📱 IDENTIFYING LEADER ARM")
        print("-"*40)
        input("\nPlease UNPLUG the LEADER arm and press ENTER...")
        
        time.sleep(1)  # Wait for USB to update
        ports_without_leader = self.list_usb_ports()
        
        # Find which port disappeared
        leader_port = None
        for port in initial_ports:
            if port not in ports_without_leader:
                leader_port = port
                break
        
        if leader_port:
            print(f"✅ Leader arm identified: {leader_port}")
        else:
            print("❌ Could not identify leader arm port")
            return None, None
        
        input("\nPlease RECONNECT the LEADER arm and press ENTER...")
        time.sleep(2)  # Wait for USB to initialize
        
        # Step 3: Identify FOLLOWER arm
        print("\n" + "-"*40)
        print("🤖 IDENTIFYING FOLLOWER ARM")
        print("-"*40)
        input("\nNow please UNPLUG the FOLLOWER arm and press ENTER...")
        
        time.sleep(1)  # Wait for USB to update
        ports_without_follower = self.list_usb_ports()
        
        # Find which port disappeared
        follower_port = None
        current_ports = self.list_usb_ports()
        for port in initial_ports:
            if port not in ports_without_follower and port != leader_port:
                follower_port = port
                break
        
        if follower_port:
            print(f"✅ Follower arm identified: {follower_port}")
        else:
            # If we can't detect it this way, use process of elimination
            for port in initial_ports:
                if port != leader_port:
                    follower_port = port
                    print(f"✅ Follower arm identified (by elimination): {follower_port}")
                    break
        
        input("\nPlease RECONNECT the FOLLOWER arm and press ENTER...")
        time.sleep(2)  # Wait for USB to initialize
        
        # Verify both ports are back
        final_ports = self.list_usb_ports()
        if leader_port not in final_ports or follower_port not in final_ports:
            print("❌ Error: Not all devices reconnected properly")
            print(f"   Expected: {leader_port}, {follower_port}")
            print(f"   Found: {final_ports}")
            return None, None
        
        print("\n" + "="*60)
        print("✅ ARM DETECTION COMPLETE")
        print(f"  Leader:   {leader_port}")
        print(f"  Follower: {follower_port}")
        print("="*60)
        
        self.leader_port = leader_port
        self.follower_port = follower_port
        
        return leader_port, follower_port
    
    def test_connection(self, port: str, arm_type: str) -> bool:
        """Test if we can connect to an arm."""
        try:
            if arm_type == "leader":
                config = SO101LeaderConfig(port=port, id="test_leader")
                arm = SO101Leader(config)
            else:
                config = SO101FollowerConfig(
                    port=port, 
                    id="test_follower",
                    enable_safety_monitoring=True  # Always use safety!
                )
                arm = SO101Follower(config)
            
            logger.info(f"Testing connection to {arm_type} on {port}...")
            arm.connect(calibrate=False)
            logger.info(f"✅ Successfully connected to {arm_type}")
            arm.disconnect()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to {arm_type} on {port}: {e}")
            return False
    
    def calibrate_follower(self, follower_port: str) -> bool:
        """Calibrate the follower arm with safety monitoring."""
        print("\n" + "="*60)
        print("🎯 CALIBRATING FOLLOWER ARM")
        print("="*60)
        
        try:
            # Create follower with safety enabled
            config = SO101FollowerConfig(
                port=follower_port,
                id="calibrated_follower",
                enable_safety_monitoring=True,
                temperature_warning=38.0,  # Conservative for calibration
                temperature_critical=42.0,
                temperature_shutdown=45.0,
            )
            
            follower = SO101Follower(config)
            
            print("\n📋 Calibration Process:")
            print("1. Connect to follower arm")
            print("2. Run calibration routine")
            print("3. Save calibration data")
            print("4. Verify calibration")
            
            # Connect and calibrate
            print("\n🔌 Connecting to follower arm...")
            follower.connect(calibrate=True)  # This will trigger calibration
            
            print("\n✅ Calibration complete!")
            
            # Test the calibration
            print("\n🧪 Testing calibration...")
            obs = follower.get_observation()
            print(f"✅ Successfully read {len(obs)} observations")
            
            # Check safety status
            if hasattr(follower, 'get_safety_status'):
                safety = follower.get_safety_status()
                print(f"\n🛡️ Safety Status: {safety['status']}")
                if 'motors' in safety:
                    for motor, data in safety['motors'].items():
                        if 'temperature' in data:
                            print(f"  • {motor}: {data['temperature']:.1f}°C")
            
            follower.disconnect()
            
            print("\n" + "="*60)
            print("✅ FOLLOWER ARM CALIBRATED SUCCESSFULLY")
            print("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Calibration failed: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure the arm is powered on")
            print("2. Check USB cable connection")
            print("3. Verify you have the correct permissions")
            print("4. Try unplugging and reconnecting the arm")
            return False
    
    def save_configuration(self):
        """Save the detected configuration for future use."""
        config_path = Path.home() / ".lerobot" / "so101_config.txt"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(f"# SO101 Auto-Detected Configuration\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"LEADER_PORT={self.leader_port}\n")
            f.write(f"FOLLOWER_PORT={self.follower_port}\n")
        
        print(f"\n💾 Configuration saved to: {config_path}")
        
        # Also print example usage
        print("\n📝 Example usage:")
        print(f"""
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

# Leader arm
leader_config = SO101LeaderConfig(
    port="{self.leader_port}",
    id="my_leader"
)
leader = SO101Leader(leader_config)

# Follower arm (with safety enabled by default!)
follower_config = SO101FollowerConfig(
    port="{self.follower_port}",
    id="my_follower",
    enable_safety_monitoring=True
)
follower = SO101Follower(follower_config)

# Connect both
leader.connect()
follower.connect()

# Your code here...

# Disconnect
leader.disconnect()
follower.disconnect()
""")
    
    def run(self):
        """Run the complete auto-calibration process."""
        print("\n" + "="*60)
        print("🤖 SO101 INTELLIGENT AUTO-CALIBRATION")
        print("="*60)
        print("\nThis script will:")
        print("  1. Check USB permissions")
        print("  2. Detect which arm is leader vs follower")
        print("  3. Calibrate the follower arm")
        print("  4. Enable safety monitoring")
        print("  5. Save configuration for future use")
        
        # Step 1: Check permissions
        print("\n" + "-"*40)
        print("Step 1: Checking permissions...")
        if not self.check_permissions():
            print("⚠️  Please fix permissions and run again.")
            if self.system == "Linux":
                print("\nQuick fix: sudo chmod 666 /dev/ttyUSB*")
            return
        print("✅ Permissions OK")
        
        # Step 2: Detect arms
        print("\n" + "-"*40)
        print("Step 2: Detecting arms...")
        leader_port, follower_port = self.detect_arms()
        
        if not leader_port or not follower_port:
            print("\n❌ Could not detect both arms. Please ensure:")
            print("  • Both arms are connected via USB")
            print("  • Both arms are powered on")
            print("  • USB cables are working")
            return
        
        # Step 3: Test connections
        print("\n" + "-"*40)
        print("Step 3: Testing connections...")
        
        if not self.test_connection(leader_port, "leader"):
            print("❌ Could not connect to leader arm")
            return
            
        if not self.test_connection(follower_port, "follower"):
            print("❌ Could not connect to follower arm")
            return
        
        print("✅ Both arms responding correctly")
        
        # Step 4: Calibrate follower
        print("\n" + "-"*40)
        print("Step 4: Calibrating follower arm...")
        
        if not self.calibrate_follower(follower_port):
            print("❌ Calibration failed")
            return
        
        # Step 5: Save configuration
        print("\n" + "-"*40)
        print("Step 5: Saving configuration...")
        self.save_configuration()
        
        # Success!
        print("\n" + "="*60)
        print("🎉 SUCCESS! Your SO101 arms are ready to use!")
        print("="*60)
        print(f"\n  Leader port:   {leader_port}")
        print(f"  Follower port: {follower_port}")
        print("\n  ✅ Follower calibrated")
        print("  ✅ Safety monitoring enabled")
        print("  ✅ Configuration saved")
        print("\nYou can now use lerobot-teleoperate with these ports!")


def main():
    """Main entry point."""
    try:
        calibrator = SO101AutoCalibrator()
        calibrator.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Calibration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()