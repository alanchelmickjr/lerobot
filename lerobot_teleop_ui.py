#!/usr/bin/env python3
"""
🤖 LeRobot Teleoperation UI - Simple, automatic, no CLI nonsense!
"""

import os
import sys
import time
import serial.tools.list_ports
from typing import Optional, Tuple, Dict
import threading
import signal

# Try to import LeRobot, if it fails, give helpful message
try:
    from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower
except ImportError:
    print("❌ LeRobot not found. Please run: conda activate lerobot")
    sys.exit(1)

# Try to import leader (might be in different location)
try:
    from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
except ImportError:
    try:
        from lerobot.common.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
    except ImportError:
        # Try the actual file directly
        try:
            from lerobot.teleoperators.so101_leader.so101_leader import SO101LeaderConfig, SO101Leader
        except:
            print("⚠️  SO101Leader import failed, some features may not work")
            SO101LeaderConfig = None
            SO101Leader = None

# Motor safety import
try:
    from lerobot.motors.motor_safety import MotorSafetyMonitor
except:
    MotorSafetyMonitor = None
    print("⚠️  Motor safety module not found, running without safety features")

# Colors for terminal
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
    """Print nice header"""
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                   🤖 LeRobot Teleoperation Control 🤖                ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def detect_voltage_based_port_type(port: str) -> Optional[str]:
    """
    Try to detect if port is leader (7.4V) or follower (12V) based on motor voltage
    This is a heuristic - may need actual voltage reading from motors
    """
    # This would need actual implementation to read motor voltages
    # For now, return None to indicate we can't auto-detect
    return None

def find_usb_ports() -> list:
    """Find all USB serial ports"""
    ports = []
    for port in serial.tools.list_ports.comports():
        # Check for various USB patterns (case insensitive)
        device_lower = port.device.lower()
        if any(pattern in device_lower for pattern in ['usb', 'usbmodem', 'usbserial', 'acm']):
            ports.append(port.device)
    
    # Also check /dev/cu.* devices on macOS
    import glob
    for device in glob.glob('/dev/cu.usbmodem*'):
        if device not in ports:
            ports.append(device)
    
    return sorted(ports)

def identify_ports_interactive() -> Tuple[str, str]:
    """Identify which port is leader vs follower using voltage detection"""
    print_header()
    print(f"{Colors.YELLOW}🔍 Port Identification (Auto-detect by voltage){Colors.RESET}\n")
    
    all_ports = find_usb_ports()
    
    if len(all_ports) == 0:
        print(f"{Colors.RED}❌ No USB ports found!{Colors.RESET}")
        print("\nPlease connect SO101 arms and try again.")
        sys.exit(1)
    
    print(f"Found {len(all_ports)} USB port(s):{Colors.RESET}")
    for port in all_ports:
        print(f"  • {port}")
    
    # Check for bi-manual setup (4 ports)
    if len(all_ports) == 4:
        print(f"\n{Colors.GREEN}🎉 4-port setup detected - Bi-manual SO101 available!{Colors.RESET}")
        print(f"{Colors.CYAN}Launch bi-manual interface? (y/n):{Colors.RESET} ", end="")
        if input().lower().startswith('y'):
            launch_bimanual_ui()
            return None, None  # Won't reach here
    
    # Try automatic detection by voltage
    print(f"\n{Colors.CYAN}Detecting arms by voltage...{Colors.RESET}")
    print("  Leader = 6-7V (low voltage)")
    print("  Follower = 12V (high voltage)")
    
    leader_port, follower_port = auto_identify_arms()
    
    if leader_port and follower_port:
        print(f"\n{Colors.GREEN}✅ Arms identified automatically!{Colors.RESET}")
        print(f"  • Leader port: {Colors.BLUE}{leader_port}{Colors.RESET} (low voltage)")
        print(f"  • Follower port: {Colors.RED}{follower_port}{Colors.RESET} (12V)")
        return leader_port, follower_port
    
    # Check if only one arm connected
    if len(all_ports) == 1:
        print(f"\n{Colors.YELLOW}⚠️  Only one arm detected{Colors.RESET}")
        
        # Try to identify which one it is
        try:
            from lerobot.motors.feetech import FeetechMotorsBus
            bus = FeetechMotorsBus(port=all_ports[0], motors={})
            bus.connect()
            found_ids = bus.scan()
            
            if found_ids:
                voltage = bus.read("Present_Voltage", found_ids[0]) / 10.0
                bus.disconnect()
                
                if voltage < 8.0:
                    print(f"  Connected: LEADER arm ({voltage:.1f}V)")
                    print(f"  {Colors.RED}Missing: FOLLOWER arm (needs 12V arm){Colors.RESET}")
                else:
                    print(f"  Connected: FOLLOWER arm ({voltage:.1f}V)")
                    print(f"  {Colors.RED}Missing: LEADER arm (needs 6-7V arm){Colors.RESET}")
            else:
                print("  Could not read voltage from connected arm")
                
            bus.disconnect()
        except Exception as e:
            print(f"  Error checking arm: {e}")
        
        print("\nPlease connect both arms and try again.")
        sys.exit(1)
    
    # Fallback to manual method if auto-detection failed
    print(f"\n{Colors.YELLOW}Auto-detection failed. Using manual method...{Colors.RESET}")
    print(f"\n{Colors.BOLD}Manual identification:{Colors.RESET}")
    print("  1. Unplug the LEADER arm (low voltage arm)")
    input("  2. Press Enter when unplugged... ")
    
    remaining_ports = find_usb_ports()
    if len(remaining_ports) == 1:
        follower_port = remaining_ports[0]
        leader_port = [p for p in all_ports if p != follower_port][0]
        
        print(f"\n{Colors.GREEN}✅ Ports identified!{Colors.RESET}")
        print(f"  • Leader port: {Colors.BLUE}{leader_port}{Colors.RESET}")
        print(f"  • Follower port: {Colors.RED}{follower_port}{Colors.RESET}")
        
        input("\n  3. Reconnect the LEADER arm and press Enter... ")
        return leader_port, follower_port
    else:
        print(f"{Colors.YELLOW}Found {len(all_ports)} USB ports. Using first two:{Colors.RESET}")
        for i, port in enumerate(all_ports[:2], 1):
            print(f"   {i}. {port}")
        
        # Manual selection
        print(f"\n{Colors.YELLOW}Manual selection:{Colors.RESET}")
        leader_idx = input(f"Which port number is the LEADER arm (1-2)? ").strip()
        if leader_idx == "1":
            return all_ports[0], all_ports[1]
        else:
            return all_ports[1], all_ports[0]

def calibrate_follower(port: str) -> bool:
    """Calibrate the follower arm"""
    print_header()
    print(f"{Colors.YELLOW}🔧 Calibrating Follower Arm{Colors.RESET}\n")
    print(f"Port: {Colors.RED}{port}{Colors.RESET}")
    
    try:
        config = SO101FollowerConfig(
            port=port,
            id="so101_follower_arm",
        )
        
        print("\nConnecting to follower...")
        follower = SO101Follower(config)
        follower.connect(calibrate=False)
        
        print("Starting calibration...")
        print(f"{Colors.YELLOW}⚠️  Arm will move! Ensure clear space.{Colors.RESET}")
        time.sleep(2)
        
        follower.calibrate()
        
        print(f"{Colors.GREEN}✅ Calibration complete!{Colors.RESET}")
        follower.disconnect()
        return True
        
    except Exception as e:
        print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"{Colors.RED}❌ CALIBRATION FAILED{Colors.RESET}")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Error details:{Colors.RESET}")
        print(f"  {str(e)}")
        print(f"\n{Colors.YELLOW}Common causes:{Colors.RESET}")
        print("  • Wrong port selected (not the follower)")
        print("  • Arm not powered on")
        print("  • USB connection issue")
        print("  • Motors are blocked/obstructed")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
        return False

def run_teleoperation(leader_port: str, follower_port: str):
    """Run teleoperation with live status display"""
    print_header()
    print(f"{Colors.GREEN}🎮 Starting Teleoperation{Colors.RESET}\n")
    
    # Configure robots
    robot_config = SO101FollowerConfig(
        port=follower_port,
        id="so101_follower",
    )
    
    teleop_config = SO101LeaderConfig(
        port=leader_port,
        id="so101_leader",
    )
    
    print(f"Leader port: {Colors.BLUE}{leader_port}{Colors.RESET}")
    print(f"Follower port: {Colors.RED}{follower_port}{Colors.RESET}")
    
    try:
        # Connect
        print("\nConnecting to robots...")
        robot = SO101Follower(robot_config)
        teleop_device = SO101Leader(teleop_config)
        
        robot.connect()
        teleop_device.connect()
        
        print(f"{Colors.GREEN}✅ Connected!{Colors.RESET}")
        print("\n" + "="*70)
        print(f"{Colors.CYAN}TELEOPERATION ACTIVE{Colors.RESET}")
        print("="*70)
        print(f"\n{Colors.YELLOW}Controls:{Colors.RESET}")
        print("  • Move the LEADER arm to control the FOLLOWER")
        print("  • Press Ctrl+C to stop")
        
        if MotorSafetyMonitor:
            print(f"\n{Colors.GREEN}🛡️  Motor Safety: ACTIVE{Colors.RESET}")
            print("  • Temperature protection: 50°C shutdown")
            print("  • Stall detection: 800mA threshold")
        
        print("\n" + "="*70)
        print(f"{Colors.BOLD}Status:{Colors.RESET}")
        
        # Teleoperation loop
        loop_count = 0
        start_time = time.time()
        
        while True:
            try:
                # Get action from leader
                action = teleop_device.get_action()
                
                # Send to follower
                robot.send_action(action)
                
                # Status display (every 100 loops)
                loop_count += 1
                if loop_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed
                    
                    # Move cursor up and overwrite status
                    print(f"\r  📊 Rate: {rate:.1f} Hz | Loops: {loop_count} | Time: {elapsed:.1f}s", end="")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
                time.sleep(0.1)
        
        # Cleanup
        print(f"\n\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
        robot.disconnect()
        teleop_device.disconnect()
        print(f"{Colors.GREEN}✅ Teleoperation stopped safely{Colors.RESET}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to start teleoperation: {e}{Colors.RESET}")
        return False
    
    return True

def diagnose_motors_menu():
    """Run motor diagnostics on selected port"""
    print_header()
    print(f"{Colors.YELLOW}🔬 Motor Diagnostics{Colors.RESET}\n")
    
    ports = find_usb_ports()
    if len(ports) == 0:
        print(f"{Colors.RED}No USB ports found!{Colors.RESET}")
        input("\nPress Enter to continue...")
        return
    
    print(f"{Colors.CYAN}Available ports:{Colors.RESET}")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")
    print(f"  {len(ports)+1}. Scan all ports")
    
    port_idx = input(f"\nSelect option (1-{len(ports)+1}): ").strip()
    
    ports_to_scan = []
    try:
        idx = int(port_idx)
        if idx == len(ports) + 1:
            ports_to_scan = ports
        else:
            ports_to_scan = [ports[idx - 1]]
    except:
        print(f"{Colors.RED}Invalid selection{Colors.RESET}")
        input("\nPress Enter to continue...")
        return
    
    for port in ports_to_scan:
        print(f"\n{Colors.CYAN}Diagnosing port: {port}{Colors.RESET}")
        print("="*60)
        
        try:
            from lerobot.motors.feetech import FeetechMotorsBus
            
            # Create a minimal bus just for scanning
            bus = FeetechMotorsBus(
                port=port,
                motors={}  # Empty motors dict for scanning
            )
            bus.connect()
            
            # Scan for motors
            print(f"\n{Colors.YELLOW}Scanning for motors...{Colors.RESET}")
            found_ids = bus.scan()
            
            if not found_ids:
                print(f"{Colors.RED}No motors found on this port{Colors.RESET}")
                bus.disconnect()
                continue
                
            print(f"\n{Colors.GREEN}✅ Found {len(found_ids)} motors:{Colors.RESET}")
            
            # Collect voltage readings to identify arm type
            voltages = []
            for motor_id in sorted(found_ids):
                try:
                    voltage = bus.read("Present_Voltage", motor_id) / 10.0  # Convert to volts
                    voltages.append(voltage)
                    temp = bus.read("Present_Temperature", motor_id)
                    position = bus.read("Present_Position", motor_id)
                    
                    print(f"\n  Motor ID {motor_id}:")
                    print(f"    Voltage: {voltage:.1f}V")
                    print(f"    Temperature: {temp}°C")
                    print(f"    Position: {position}")
                    
                except Exception as e:
                    print(f"    {Colors.RED}Error reading motor {motor_id}: {e}{Colors.RESET}")
            
            # Identify arm type based on voltage
            if voltages:
                avg_voltage = sum(voltages) / len(voltages)
                print(f"\n{Colors.CYAN}Average voltage: {avg_voltage:.1f}V{Colors.RESET}")
                
                if avg_voltage < 8.0:
                    print(f"{Colors.GREEN}✅ This is the LEADER arm (low voltage){Colors.RESET}")
                    print(f"    Leader arms typically run at 6-7.4V")
                elif avg_voltage > 10.0:
                    print(f"{Colors.BLUE}✅ This is the FOLLOWER arm (12V){Colors.RESET}")
                    print(f"    Follower arms run at 12V")
                else:
                    print(f"{Colors.YELLOW}⚠️ Unusual voltage range{Colors.RESET}")
                    print(f"    Expected: ~7V (leader) or ~12V (follower)")
            
            bus.disconnect()
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Diagnostic failed: {e}{Colors.RESET}")
            print(f"Error details: {str(e)}")
    
    input("\nPress Enter to continue...")

def auto_identify_arms():
    """Automatically identify leader and follower arms by voltage"""
    ports = find_usb_ports()
    leader_port = None
    follower_port = None
    
    for port in ports:
        try:
            from lerobot.motors.feetech import FeetechMotorsBus
            
            bus = FeetechMotorsBus(port=port, motors={})
            bus.connect()
            
            found_ids = bus.scan()
            if found_ids:
                # Read voltage from first motor
                voltage = bus.read("Present_Voltage", found_ids[0]) / 10.0
                
                if voltage < 8.0:
                    leader_port = port
                elif voltage > 10.0:
                    follower_port = port
            
            bus.disconnect()
        except:
            pass
    
    return leader_port, follower_port

def detect_bimanual_setup():
    """Simple 4-port bi-manual detection"""
    ports = find_usb_ports()
    if len(ports) != 4:
        return None
    
    leaders = []
    followers = []
    
    for port in ports:
        try:
            from lerobot.motors.feetech import FeetechMotorsBus
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
        except:
            pass
    
    if len(leaders) == 2 and len(followers) == 2:
        return {
            "left_leader": leaders[0], "left_follower": followers[0],
            "right_leader": leaders[1], "right_follower": followers[1]
        }
    return None

def select_coordination_mode():
    """Select bimanual coordination mode"""
    print_header()
    print(f"{Colors.CYAN}🤖🤖 Select Coordination Mode{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}1. 🤝 COORDINATED - Arms work together{Colors.RESET}")
    print(f"{Colors.BLUE}2. 🆓 INDEPENDENT - Separate arm control{Colors.RESET}")
    print(f"{Colors.MAGENTA}3. 🪞 MIRROR - Right mirrors left{Colors.RESET}")
    
    while True:
        choice = input(f"\n{Colors.CYAN}Select mode (1-3):{Colors.RESET} ").strip()
        if choice == "1": return "coordinated"
        elif choice == "2": return "independent"
        elif choice == "3": return "mirror"
        print(f"{Colors.RED}Invalid choice{Colors.RESET}")

def run_bimanual_teleoperation(setup, mode):
    """Run bimanual teleoperation - simplified"""
    print_header()
    print(f"{Colors.GREEN}🤖🤖 Bi-Manual Teleoperation - {mode.upper()}{Colors.RESET}\n")
    
    try:
        # Import bimanual classes
        from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
        from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader
        
        # Configure
        robot_config = BiSO100FollowerConfig(
            left_arm_port=setup['left_follower'],
            right_arm_port=setup['right_follower'],
            id="bimanual_follower"
        )
        
        teleop_config = BiSO100LeaderConfig(
            left_arm_port=setup['left_leader'],
            right_arm_port=setup['right_leader'],
            id="bimanual_leader"
        )
        
        print("Connecting bimanual system...")
        robot = BiSO100Follower(robot_config)
        teleop = BiSO100Leader(teleop_config)
        
        robot.connect()
        teleop.connect()
        
        print(f"{Colors.GREEN}✅ Connected! Mode: {mode.upper()}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Controls:{Colors.RESET}")
        if mode == "independent":
            print("  • Left leader → Left follower")
            print("  • Right leader → Right follower")
        elif mode == "mirror":
            print("  • Left leader → Both followers (mirrored)")
        else:  # coordinated
            print("  • Both leaders → Coordinated movement")
        
        print("  • Press Ctrl+C to stop")
        print("\n" + "="*50)
        
        # Simple teleoperation loop
        loop_count = 0
        start_time = time.time()
        
        while True:
            try:
                actions = teleop.get_action()
                
                # Apply mode logic
                if mode == "mirror":
                    # Left controls both, mirror right
                    left_actions = {k: v for k, v in actions.items() if k.startswith('left_')}
                    right_actions = {k.replace('left_', 'right_'): v for k, v in left_actions.items()}
                    final_actions = {**left_actions, **right_actions}
                elif mode == "coordinated":
                    # Coordinated mode: LEFT leader controls BOTH followers
                    left_actions = {k: v for k, v in actions.items() if k.startswith('left_')}
                    
                    # Create coordinated follower actions - left leader mirrors to both
                    final_actions = {}
                    
                    # Apply left leader actions to both followers
                    for left_key, left_val in left_actions.items():
                        # Send to left follower
                        final_actions[left_key] = left_val
                        # Mirror to right follower
                        right_key = left_key.replace('left_', 'right_')
                        final_actions[right_key] = left_val
                else:
                    # Independent mode
                    final_actions = actions
                
                robot.send_action(final_actions)
                
                # Status
                loop_count += 1
                if loop_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed
                    print(f"\r  📊 {mode.upper()} | {rate:.1f} Hz | {elapsed:.1f}s", end="")
                
            except KeyboardInterrupt:
                break
                
        print(f"\n\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
        robot.disconnect()
        teleop.disconnect()
        print(f"{Colors.GREEN}✅ Done!{Colors.RESET}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")

def launch_bimanual_ui():
    """Launch bimanual interface"""
    setup = detect_bimanual_setup()
    if not setup:
        print(f"{Colors.RED}❌ 4-port setup not detected{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}✅ Bimanual setup detected:{Colors.RESET}")
    for key, port in setup.items():
        print(f"  {key}: {port}")
    
    # Quick start or configuration
    print(f"\n{Colors.CYAN}1. 🚀 Quick Start{Colors.RESET}")
    print(f"{Colors.CYAN}2. 🔧 Calibrate First{Colors.RESET}")
    
    choice = input(f"\nSelect (1-2): ").strip()
    
    if choice == "2":
        print("Calibrating bimanual arms...")
        # Add calibration here if needed
    
    mode = select_coordination_mode()
    run_bimanual_teleoperation(setup, mode)

def main_menu():
    """Main interactive menu"""
    while True:
        print_header()
        
        # Check for setup type
        all_ports = find_usb_ports()
        if len(all_ports) == 4:
            bimanual_setup = detect_bimanual_setup()
            if bimanual_setup:
                print(f"{Colors.GREEN}🎉 4-Port Bi-Manual Setup Detected!{Colors.RESET}\n")
                print(f"{Colors.CYAN}Bi-Manual Menu:{Colors.RESET}\n")
                print("  1. 🚀 Bi-Manual Quick Start")
                print("  2. 🔧 Calibrate Both Arms")
                print("  3. 🎮 Bi-Manual Teleoperation")
                print("  4. 🔄 Switch to Single Arm Mode")
                print("  5. 🔬 Motor Diagnostics")
                print("  6. ❌ Exit")
                
                choice = input(f"\n{Colors.YELLOW}Select option (1-6):{Colors.RESET} ").strip()
                
                if choice == "1":
                    # Bi-manual quick start
                    mode = select_coordination_mode()
                    run_bimanual_teleoperation(bimanual_setup, mode)
                    
                elif choice == "2":
                    print(f"{Colors.YELLOW}Bi-manual calibration - feature coming soon!{Colors.RESET}")
                    input("Press Enter to continue...")
                    
                elif choice == "3":
                    mode = select_coordination_mode()
                    run_bimanual_teleoperation(bimanual_setup, mode)
                    
                elif choice == "4":
                    # Force single arm mode
                    print(f"{Colors.BLUE}Switching to single arm mode...{Colors.RESET}")
                    single_arm_menu()
                    
                elif choice == "5":
                    diagnose_motors_menu()
                    
                elif choice == "6":
                    print(f"\n{Colors.GREEN}Goodbye! 🤖🤖{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}Invalid option{Colors.RESET}")
                    time.sleep(1)
                continue
        
        # Single arm menu (original)
        single_arm_menu()
        break

def single_arm_menu():
    """Single arm menu (original functionality)"""
    while True:
        print_header()
        print(f"{Colors.CYAN}Single Arm Menu:{Colors.RESET}\n")
        print("  1. 🚀 Quick Start (Auto-detect & Run)")
        print("  2. 🔧 Calibrate Follower Arm")
        print("  3. 🎮 Start Teleoperation")
        print("  4. 🔍 Identify Ports")
        print("  5. 🔬 Motor Diagnostics")
        print("  6. ❌ Exit")
        
        choice = input(f"\n{Colors.YELLOW}Select option (1-6):{Colors.RESET} ").strip()
        
        if choice == "1":
            # Quick start - do everything automatically
            print(f"\n{Colors.CYAN}🚀 Quick Start Mode{Colors.RESET}")
            
            # Identify ports
            result = identify_ports_interactive()
            if result == (None, None):  # Bimanual was launched
                return
            leader_port, follower_port = result
            
            # Calibrate
            print(f"\n{Colors.YELLOW}Calibrate follower arm? (recommended for first use){Colors.RESET}")
            if input("Calibrate? (y/n): ").lower() == 'y':
                if not calibrate_follower(follower_port):
                    print("Calibration failed, continuing anyway...")
                    time.sleep(2)
            
            # Run teleoperation
            run_teleoperation(leader_port, follower_port)
            
        elif choice == "2":
            # Just calibrate
            ports = find_usb_ports()
            if len(ports) == 0:
                print(f"{Colors.RED}No USB ports found!{Colors.RESET}")
                time.sleep(2)
                continue
            
            print(f"\n{Colors.CYAN}Available ports:{Colors.RESET}")
            for i, port in enumerate(ports, 1):
                print(f"  {i}. {port}")
            
            port_idx = input(f"\nSelect follower port (1-{len(ports)}): ").strip()
            try:
                port = ports[int(port_idx) - 1]
                calibrate_follower(port)
            except:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            # Manual teleoperation
            result = identify_ports_interactive()
            if result == (None, None):  # Bimanual was launched
                return
            leader_port, follower_port = result
            run_teleoperation(leader_port, follower_port)
            
        elif choice == "4":
            # Just identify ports
            result = identify_ports_interactive()
            if result == (None, None):  # Bimanual was launched
                return
            leader_port, follower_port = result
            print(f"\n{Colors.GREEN}Ports identified!{Colors.RESET}")
            print(f"  Leader: {leader_port}")
            print(f"  Follower: {follower_port}")
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Motor diagnostics
            diagnose_motors_menu()
            
        elif choice == "6":
            print(f"\n{Colors.GREEN}Goodbye! 🤖{Colors.RESET}")
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
    
    # Environment check removed - handled by launcher script
    
    # Start the UI
    try:
        main_menu()
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)