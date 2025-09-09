#!/usr/bin/env python3
"""
Motor Diagnostic Tool for SO101 Arms
"""

import sys
from lerobot.motors.feetech import FeetechMotorsBus

def diagnose_motors(port):
    """Diagnose motors on a given port"""
    print(f"\n🔍 Diagnosing motors on port: {port}")
    print("="*60)
    
    try:
        # Create a basic bus connection
        bus = FeetechMotorsBus(port=port, motors={})
        bus.connect()
        
        # Scan for all motors
        print("\n📡 Scanning for motors...")
        found_motors = bus.scan()
        
        print(f"\n✅ Found {len(found_motors)} motors:")
        for motor_id in sorted(found_motors):
            # Read motor info
            model = bus.read("Model_Number", motor_id)
            voltage = bus.read("Present_Voltage", motor_id) / 10.0  # Convert to volts
            temp = bus.read("Present_Temperature", motor_id)
            
            # Determine motor type
            if model == 777:
                model_name = "STS3215 (standard)"
            elif model == 1033:
                model_name = "Different model (1033)"
            else:
                model_name = f"Unknown ({model})"
            
            print(f"  Motor {motor_id}: {model_name}")
            print(f"    - Voltage: {voltage:.1f}V")
            print(f"    - Temperature: {temp}°C")
            
            # Check for issues
            if motor_id == 4 and model != 777:
                print(f"    ⚠️  ISSUE: Motor 4 has wrong model number!")
                print(f"       Expected: 777 (STS3215)")
                print(f"       Found: {model}")
                print(f"       Solutions:")
                print(f"         1. Replace motor 4 with correct model")
                print(f"         2. Reconfigure motor 4's ID/model")
                print(f"         3. Check wiring between motor 3 and 4")
        
        bus.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_motor.py <port>")
        print("Example: python diagnose_motor.py /dev/cu.usbmodem5A7A0185761")
        sys.exit(1)
    
    port = sys.argv[1]
    diagnose_motors(port)