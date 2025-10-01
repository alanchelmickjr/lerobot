#!/usr/bin/env python3
"""
🧪 Bi-Manual SO101 Setup Test Script
Quick verification that your 4-arm setup is ready for touch control!
"""

import sys
import time
import serial.tools.list_ports
from typing import Dict, List

# Colors for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              🧪 Bi-Manual SO101 Setup Test 🧪                        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

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

def test_port_voltage(port: str) -> Dict:
    """Test a single port and return voltage info"""
    result = {
        'port': port,
        'status': 'unknown',
        'voltage': None,
        'motor_count': 0,
        'arm_type': 'unknown'
    }
    
    try:
        from lerobot.motors.feetech import FeetechMotorsBus
        
        print(f"  Testing {port}... ", end="", flush=True)
        
        bus = FeetechMotorsBus(port=port, motors={})
        bus.connect()
        
        # Scan for motors
        found_ids = bus.scan()
        result['motor_count'] = len(found_ids)
        
        if found_ids:
            # Read voltage from first motor
            voltage = bus.read("Present_Voltage", found_ids[0]) / 10.0
            result['voltage'] = voltage
            result['status'] = 'connected'
            
            # Determine arm type
            if voltage < 8.0:
                result['arm_type'] = 'leader'
                print(f"{Colors.GREEN}LEADER ({voltage:.1f}V, {len(found_ids)} motors){Colors.RESET}")
            elif voltage > 10.0:
                result['arm_type'] = 'follower' 
                print(f"{Colors.BLUE}FOLLOWER ({voltage:.1f}V, {len(found_ids)} motors){Colors.RESET}")
            else:
                result['arm_type'] = 'unknown_voltage'
                print(f"{Colors.YELLOW}UNKNOWN ({voltage:.1f}V, {len(found_ids)} motors){Colors.RESET}")
        else:
            result['status'] = 'no_motors'
            print(f"{Colors.RED}NO MOTORS FOUND{Colors.RESET}")
        
        bus.disconnect()
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        print(f"{Colors.RED}ERROR: {e}{Colors.RESET}")
    
    return result

def test_bimanual_compatibility():
    """Test if bi-manual classes can be imported"""
    print(f"{Colors.YELLOW}Testing LeRobot bi-manual imports...{Colors.RESET}")
    
    try:
        from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
        print(f"  {Colors.GREEN}✓ BiSO100Follower imported successfully{Colors.RESET}")
        
        from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader  
        print(f"  {Colors.GREEN}✓ BiSO100Leader imported successfully{Colors.RESET}")
        
        from lerobot.motors.feetech import FeetechMotorsBus
        print(f"  {Colors.GREEN}✓ FeetechMotorsBus imported successfully{Colors.RESET}")
        
        return True
        
    except ImportError as e:
        print(f"  {Colors.RED}❌ Import failed: {e}{Colors.RESET}")
        return False

def analyze_setup(results: List[Dict]) -> Dict:
    """Analyze the port test results"""
    leaders = [r for r in results if r['arm_type'] == 'leader']
    followers = [r for r in results if r['arm_type'] == 'follower'] 
    errors = [r for r in results if r['status'] == 'error']
    
    analysis = {
        'total_ports': len(results),
        'leaders': len(leaders),
        'followers': len(followers), 
        'errors': len(errors),
        'bimanual_ready': len(leaders) == 2 and len(followers) == 2,
        'single_ready': len(leaders) >= 1 and len(followers) >= 1
    }
    
    return analysis

def main():
    print_header()
    
    # Test 1: Check imports
    print(f"{Colors.CYAN}[1/3] 🔍 Testing LeRobot imports...{Colors.RESET}")
    if not test_bimanual_compatibility():
        print(f"\n{Colors.RED}❌ LeRobot components not available. Please activate conda environment:{Colors.RESET}")
        print("  conda activate lerobot")
        sys.exit(1)
    
    print(f"\n{Colors.CYAN}[2/3] 🔌 Scanning USB ports...{Colors.RESET}")
    
    # Test 2: Find and test ports
    ports = find_usb_ports()
    
    if not ports:
        print(f"{Colors.RED}❌ No USB ports found!{Colors.RESET}")
        print("Please connect your SO101 arms and try again.")
        sys.exit(1)
    
    print(f"Found {len(ports)} USB port(s):")
    
    # Test each port
    results = []
    for port in ports:
        result = test_port_voltage(port)
        results.append(result)
    
    print(f"\n{Colors.CYAN}[3/3] 📊 Analyzing setup...{Colors.RESET}")
    
    # Test 3: Analyze results
    analysis = analyze_setup(results)
    
    print(f"\nSetup Analysis:")
    print(f"  Total ports: {analysis['total_ports']}")
    print(f"  Leader arms: {Colors.GREEN if analysis['leaders'] > 0 else Colors.RED}{analysis['leaders']}{Colors.RESET}")
    print(f"  Follower arms: {Colors.BLUE if analysis['followers'] > 0 else Colors.RED}{analysis['followers']}{Colors.RESET}")
    print(f"  Errors: {Colors.RED if analysis['errors'] > 0 else Colors.GREEN}{analysis['errors']}{Colors.RESET}")
    
    # Final verdict
    print(f"\n{Colors.BOLD}🎯 VERDICT:{Colors.RESET}")
    
    if analysis['bimanual_ready']:
        print(f"{Colors.GREEN}🎉 BI-MANUAL READY! You have 2 leaders + 2 followers{Colors.RESET}")
        print(f"\n{Colors.CYAN}🚀 Ready to launch:{Colors.RESET}")
        print("  ./start_lerobot_touch.sh")
        
        # Show the configuration  
        leaders = [r for r in results if r['arm_type'] == 'leader']
        followers = [r for r in results if r['arm_type'] == 'follower']
        
        print(f"\n{Colors.YELLOW}Detected Configuration:{Colors.RESET}")
        print(f"  Left Leader: {leaders[0]['port']} ({leaders[0]['voltage']:.1f}V)")
        print(f"  Left Follower: {followers[0]['port']} ({followers[0]['voltage']:.1f}V)")
        print(f"  Right Leader: {leaders[1]['port']} ({leaders[1]['voltage']:.1f}V)")  
        print(f"  Right Follower: {followers[1]['port']} ({followers[1]['voltage']:.1f}V)")
        
    elif analysis['single_ready']:
        print(f"{Colors.YELLOW}⚡ SINGLE ARM READY - Need 2 more arms for bi-manual{Colors.RESET}")
        print(f"Current: {analysis['leaders']} leader(s) + {analysis['followers']} follower(s)")
        print(f"Need: 2 leaders + 2 followers for bi-manual mode")
        
    else:
        print(f"{Colors.RED}❌ NOT READY - Check connections and power{Colors.RESET}")
        print("Make sure your SO101 arms are:")
        print("  • Properly connected via USB")
        print("  • Powered on")
        print("  • Have different voltages (leaders ~7V, followers ~12V)")
    
    print(f"\n{Colors.CYAN}Test complete! 🧪{Colors.RESET}")

if __name__ == "__main__":
    main()