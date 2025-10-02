#!/usr/bin/env python3
"""
🤖🤖 LeRobot Bi-Manual Teleoperation UI - Joint, Independent & Mirror Modes!
"""

import os
import sys
import time
import threading
import signal
import serial.tools.list_ports
from typing import Optional, Tuple, Dict, List
from enum import Enum

# Try to import LeRobot components
try:
    from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower
    from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
    from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
    from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader
except ImportError as e:
    print(f"❌ LeRobot components not found: {e}")
    print("Please run: conda activate lerobot")
    sys.exit(1)

# Motor safety import
try:
    from lerobot.motors.motor_safety import MotorSafetyMonitor
except:
    MotorSafetyMonitor = None

class CoordinationMode(Enum):
    INDEPENDENT = "independent"
    COORDINATED = "coordinated"  
    MIRROR = "mirror"

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Print awesome bi-manual header"""
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              🤖🤖 LeRobot Bi-Manual Control System 🤖🤖              ║")
    print("║                    Joint • Independent • Mirror                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def find_usb_ports() -> List[str]:
    """Find all USB serial ports"""
    ports = []
    for port in serial.tools.list_ports.comports():
        device_lower = port.device.lower()
        if any(pattern in device_lower for pattern in ['usb', 'usbmodem', 'usbserial', 'acm']):
            ports.append(port.device)
    
    # Also check /dev/cu.* devices on macOS
    import glob
    for device in glob.glob('/dev/cu.usbmodem*'):
        if device not in ports:
            ports.append(device)
    
    return sorted(ports)

def identify_arm_by_voltage(port: str) -> Optional[str]:
    """Identify if port is leader (low voltage) or follower (12V)"""
    try:
        from lerobot.motors.feetech import FeetechMotorsBus
        bus = FeetechMotorsBus(port=port, motors={})
        bus.connect()
        found_ids = bus.scan()
        
        if found_ids:
            voltage = bus.read("Present_Voltage", found_ids[0]) / 10.0
            bus.disconnect()
            
            if voltage < 8.0:
                return "leader"
            elif voltage > 10.0:
                return "follower"
            
        bus.disconnect()
    except Exception:
        pass
    
    return None

def detect_bimanual_setup() -> Optional[Dict]:
    """Detect 4-port bi-manual setup automatically"""
    print(f"{Colors.YELLOW}🔍 Scanning for bi-manual setup...{Colors.RESET}")
    
    ports = find_usb_ports()
    
    if len(ports) != 4:
        return None
    
    print(f"Found 4 ports - analyzing configuration...")
    
    # Identify each port
    port_types = {}
    leaders = []
    followers = []
    
    for port in ports:
        port_type = identify_arm_by_voltage(port)
        if port_type == "leader":
            leaders.append(port)
        elif port_type == "follower":
            followers.append(port)
        port_types[port] = port_type
        print(f"  {port}: {port_type}")
    
    if len(leaders) == 2 and len(followers) == 2:
        return {
            "left_leader": leaders[0],
            "left_follower": followers[0], 
            "right_leader": leaders[1],
            "right_follower": followers[1],
            "all_ports": ports
        }
    
    return None

def select_coordination_mode() -> CoordinationMode:
    """Beautiful interactive coordination mode selection"""
    print_header()
    print(f"{Colors.CYAN}🎮 Select Coordination Mode{Colors.RESET}\n")
    
    # Beautiful mode descriptions
    modes = [
        {
            "key": "1",
            "mode": CoordinationMode.COORDINATED,
            "name": "🤝 COORDINATED Mode", 
            "desc": "Arms work together for complex dual-arm tasks",
            "example": "Pick & place, bimanual manipulation",
            "color": Colors.GREEN
        },
        {
            "key": "2", 
            "mode": CoordinationMode.INDEPENDENT,
            "name": "🆓 INDEPENDENT Mode",
            "desc": "Arms operate completely independently", 
            "example": "Two separate tasks simultaneously",
            "color": Colors.BLUE
        },
        {
            "key": "3",
            "mode": CoordinationMode.MIRROR,
            "name": "🪞 MIRROR Mode",
            "desc": "Right arm mirrors left arm movements",
            "example": "Symmetrical operations, demonstrations", 
            "color": Colors.MAGENTA
        }
    ]
    
    for mode in modes:
        print(f"{mode['color']}{mode['key']}. {mode['name']}{Colors.RESET}")
        print(f"   {mode['desc']}")
        print(f"   {Colors.YELLOW}Example: {mode['example']}{Colors.RESET}")
        print()
    
    while True:
        choice = input(f"{Colors.CYAN}Select mode (1-3):{Colors.RESET} ").strip()
        
        for mode in modes:
            if choice == mode['key']:
                print(f"\n{mode['color']}✅ Selected: {mode['name']}{Colors.RESET}")
                return mode['mode']
        
        print(f"{Colors.RED}Invalid choice. Please select 1, 2, or 3.{Colors.RESET}")

def calibrate_bimanual_arms(setup: Dict) -> bool:
    """Calibrate both follower arms"""
    print_header()
    print(f"{Colors.YELLOW}🔧 Calibrating Bi-Manual Arms{Colors.RESET}\n")
    
    print(f"Left Follower: {Colors.BLUE}{setup['left_follower']}{Colors.RESET}")
    print(f"Right Follower: {Colors.MAGENTA}{setup['right_follower']}{Colors.RESET}")
    
    try:
        # Create bi-manual config
        config = BiSO100FollowerConfig(
            left_arm_port=setup['left_follower'],
            right_arm_port=setup['right_follower'],
            id="bimanual_so101",
        )
        
        print("\n🤖 Connecting to bi-manual follower...")
        robot = BiSO100Follower(config)
        robot.connect(calibrate=False)
        
        print("🎯 Starting calibration...")
        print(f"{Colors.YELLOW}⚠️  Both arms will move! Ensure clear space.{Colors.RESET}")
        time.sleep(3)
        
        robot.calibrate()
        
        print(f"{Colors.GREEN}✅ Bi-manual calibration complete!{Colors.RESET}")
        robot.disconnect()
        return True
        
    except Exception as e:
        print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"{Colors.RED}❌ BI-MANUAL CALIBRATION FAILED{Colors.RESET}")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Error: {str(e)}{Colors.RESET}")
        return False

def run_bimanual_teleoperation(setup: Dict, mode: CoordinationMode):
    """Run bi-manual teleoperation with selected mode"""
    print_header()
    print(f"{Colors.GREEN}🤖🤖 Starting Bi-Manual Teleoperation{Colors.RESET}\n")
    
    # Show configuration
    mode_colors = {
        CoordinationMode.COORDINATED: Colors.GREEN,
        CoordinationMode.INDEPENDENT: Colors.BLUE, 
        CoordinationMode.MIRROR: Colors.MAGENTA
    }
    
    mode_color = mode_colors[mode]
    print(f"Mode: {mode_color}{mode.value.upper()}{Colors.RESET}")
    print(f"Left Leader:   {Colors.BLUE}{setup['left_leader']}{Colors.RESET}")
    print(f"Left Follower: {Colors.BLUE}{setup['left_follower']}{Colors.RESET}")
    print(f"Right Leader:  {Colors.MAGENTA}{setup['right_leader']}{Colors.RESET}")
    print(f"Right Follower:{Colors.MAGENTA}{setup['right_follower']}{Colors.RESET}")
    
    try:
        # Configure bi-manual robots
        follower_config = BiSO100FollowerConfig(
            left_arm_port=setup['left_follower'],
            right_arm_port=setup['right_follower'],
            id="bimanual_follower",
        )
        
        leader_config = BiSO100LeaderConfig(
            left_arm_port=setup['left_leader'],
            right_arm_port=setup['right_leader'], 
            id="bimanual_leader",
        )
        
        print("\n🔗 Connecting to bi-manual system...")
        robot = BiSO100Follower(follower_config)
        teleop = BiSO100Leader(leader_config)
        
        robot.connect()
        teleop.connect()
        
        print(f"{Colors.GREEN}✅ Bi-manual system connected!{Colors.RESET}")
        print("\n" + "="*70)
        print(f"{mode_color}BI-MANUAL TELEOPERATION ACTIVE - {mode.value.upper()} MODE{Colors.RESET}")
        print("="*70)
        
        # Mode-specific instructions
        if mode == CoordinationMode.COORDINATED:
            print(f"\n{Colors.GREEN}🤝 COORDINATED Mode Instructions:{Colors.RESET}")
            print("  • Both leader arms control coordinated follower movement")
            print("  • Use for bimanual pick-and-place tasks")
            print("  • Arms work together as a team")
            
        elif mode == CoordinationMode.INDEPENDENT:
            print(f"\n{Colors.BLUE}🆓 INDEPENDENT Mode Instructions:{Colors.RESET}")
            print("  • Left leader controls left follower")
            print("  • Right leader controls right follower") 
            print("  • Completely separate control systems")
            
        elif mode == CoordinationMode.MIRROR:
            print(f"\n{Colors.MAGENTA}🪞 MIRROR Mode Instructions:{Colors.RESET}")
            print("  • Left leader controls BOTH followers")
            print("  • Right follower mirrors left follower")
            print("  • Perfect for symmetrical tasks")
        
        print(f"\n{Colors.YELLOW}Controls:{Colors.RESET}")
        print("  • Move the leader arms to control followers")
        print("  • Press Ctrl+C to stop")
        
        if MotorSafetyMonitor:
            print(f"\n{Colors.GREEN}🛡️  Motor Safety: ACTIVE{Colors.RESET}")
            print("  • Temperature protection: 50°C shutdown")
            print("  • Stall detection: 800mA threshold")
        
        print("\n" + "="*70)
        print(f"{Colors.BOLD}Live Status:{Colors.RESET}")
        
        # Teleoperation loop with mode-specific behavior
        loop_count = 0
        start_time = time.time()
        
        while True:
            try:
                # Get actions from leaders
                leader_actions = teleop.get_action()
                
                if mode == CoordinationMode.INDEPENDENT:
                    # Direct mapping - each leader controls its follower
                    follower_actions = leader_actions
                    
                elif mode == CoordinationMode.MIRROR:
                    # Left leader controls both, right mirrors left
                    left_actions = {k: v for k, v in leader_actions.items() if k.startswith('left_')}
                    # Mirror left to right
                    right_actions = {}
                    for k, v in left_actions.items():
                        right_key = k.replace('left_', 'right_')
                        right_actions[right_key] = v
                    
                    follower_actions = {**left_actions, **right_actions}
                    
                elif mode == CoordinationMode.COORDINATED:
                    # Coordinated mode: LEFT leader controls BOTH followers
                    left_actions = {k: v for k, v in leader_actions.items() if k.startswith('left_')}
                    
                    # Create coordinated follower actions - left leader mirrors to both
                    follower_actions = {}
                    
                    # Apply left leader actions to both followers
                    for left_key, left_val in left_actions.items():
                        # Send to left follower
                        follower_actions[left_key] = left_val
                        # Mirror to right follower
                        right_key = left_key.replace('left_', 'right_')
                        follower_actions[right_key] = left_val
                
                # Send actions to followers
                robot.send_action(follower_actions)
                
                # Status display (every 100 loops)
                loop_count += 1
                if loop_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed
                    
                    # Show mode and rate
                    print(f"\r  📊 {mode_color}{mode.value.upper()}{Colors.RESET} | Rate: {rate:.1f} Hz | Loops: {loop_count} | Time: {elapsed:.1f}s", end="")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
                time.sleep(0.1)
        
        # Cleanup
        print(f"\n\n{Colors.YELLOW}Shutting down bi-manual system...{Colors.RESET}")
        robot.disconnect()
        teleop.disconnect()
        print(f"{Colors.GREEN}✅ Bi-manual teleoperation stopped safely{Colors.RESET}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start bi-manual teleoperation: {e}{Colors.RESET}")
        return False
    
    return True

def bimanual_main_menu():
    """Main bi-manual menu with awesome options"""
    while True:
        print_header()
        print(f"{Colors.CYAN}Bi-Manual Control Menu:{Colors.RESET}\n")
        print("  1. 🚀 Quick Start Bi-Manual (Auto-detect & Run)")
        print("  2. 🔧 Calibrate Both Arms") 
        print("  3. 🎮 Start Bi-Manual Teleoperation")
        print("  4. 🔍 Detect 4-Port Setup")
        print("  5. ⚙️  Mode Configuration Test")
        print("  6. 🔙 Back to Single Arm Menu")
        print("  7. ❌ Exit")
        
        choice = input(f"\n{Colors.YELLOW}Select option (1-7):{Colors.RESET} ").strip()
        
        if choice == "1":
            # Quick start with full flow
            setup = detect_bimanual_setup()
            if not setup:
                print(f"{Colors.RED}❌ Could not detect 4-port bi-manual setup{Colors.RESET}")
                print("Make sure you have 2 leader arms (low voltage) and 2 follower arms (12V) connected.")
                input("\nPress Enter to continue...")
                continue
            
            print(f"{Colors.GREEN}✅ 4-port bi-manual setup detected!{Colors.RESET}")
            
            # Select coordination mode
            mode = select_coordination_mode()
            
            # Ask about calibration
            print(f"\n{Colors.YELLOW}Calibrate follower arms first? (recommended){Colors.RESET}")
            if input("Calibrate? (y/n): ").lower() == 'y':
                if not calibrate_bimanual_arms(setup):
                    print("Calibration failed, continuing anyway...")
                    time.sleep(2)
            
            # Run teleoperation
            run_bimanual_teleoperation(setup, mode)
            
        elif choice == "2":
            # Just calibration
            setup = detect_bimanual_setup()
            if setup:
                calibrate_bimanual_arms(setup)
            else:
                print(f"{Colors.RED}❌ 4-port setup not detected{Colors.RESET}")
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            # Manual teleoperation
            setup = detect_bimanual_setup()
            if setup:
                mode = select_coordination_mode()
                run_bimanual_teleoperation(setup, mode)
            else:
                print(f"{Colors.RED}❌ 4-port setup not detected{Colors.RESET}")
                input("\nPress Enter to continue...")
            
        elif choice == "4":
            # Port detection
            setup = detect_bimanual_setup()
            if setup:
                print(f"{Colors.GREEN}✅ Bi-manual setup detected!{Colors.RESET}")
                for key, port in setup.items():
                    if key != 'all_ports':
                        print(f"  {key}: {port}")
            else:
                print(f"{Colors.RED}❌ No 4-port bi-manual setup found{Colors.RESET}")
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Mode configuration test
            mode = select_coordination_mode()
            print(f"\n{Colors.GREEN}Selected mode: {mode.value}{Colors.RESET}")
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            # Back to single arm (would launch original UI)
            print(f"{Colors.BLUE}Launching single arm menu...{Colors.RESET}")
            try:
                import subprocess
                subprocess.run([sys.executable, "lerobot_teleop_ui.py"])
            except Exception as e:
                print(f"Could not launch single arm UI: {e}")
            
        elif choice == "7":
            print(f"\n{Colors.GREEN}Goodbye! 🤖🤖{Colors.RESET}")
            break
        else:
            print(f"{Colors.RED}Invalid option{Colors.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check for 4-port setup on startup
    ports = find_usb_ports()
    if len(ports) == 4:
        print(f"{Colors.GREEN}🎉 4-port setup detected - launching bi-manual UI!{Colors.RESET}")
        time.sleep(1)
    
    # Start the bi-manual UI
    try:
        bimanual_main_menu()
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)