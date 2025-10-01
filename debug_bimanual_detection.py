#!/usr/bin/env python3
"""
Debug script to test bi-manual detection without GUI
"""
import os
import glob
import time
from pathlib import Path

def scan_usb_ports():
    """Scan for USB ports and detect bi-manual setup"""
    print(f"🔍 Scanning USB ports at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Find all ttyACM ports
    acm_ports = sorted(glob.glob('/dev/ttyACM*'))
    print(f"📱 Found {len(acm_ports)} ACM ports: {acm_ports}")
    
    if len(acm_ports) == 4:
        print("🤖🤖 BI-MANUAL SETUP DETECTED! 4 ports found:")
        print("   ACM0: Left Leader")
        print("   ACM1: Right Leader") 
        print("   ACM2: Left Follower")
        print("   ACM3: Right Follower")
        return True
    elif len(acm_ports) == 2:
        print("🤖 Single arm setup detected (2 ports)")
        return False
    else:
        print(f"❌ Unexpected port count: {len(acm_ports)}")
        return False

def test_lerobot_imports():
    """Test LeRobot imports"""
    print("\n🧪 Testing LeRobot imports...")
    
    try:
        import sys
        sys.path.append('/home/feetech/lerobot/src')
        
        from lerobot.robots.bi_so100_follower import BiSO100Follower
        from lerobot.teleoperators.bi_so100_leader import BiSO100Leader
        print("✅ LeRobot bi-manual imports successful!")
        return True
    except ImportError as e:
        print(f"❌ LeRobot import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🚀 BI-MANUAL DETECTION DEBUG TOOL")
    print("=" * 50)
    
    # Test USB detection
    bi_manual_ready = scan_usb_ports()
    
    # Test imports
    imports_ok = test_lerobot_imports()
    
    print("\n📊 SUMMARY:")
    print(f"   🔌 Bi-manual hardware: {'✅ READY' if bi_manual_ready else '❌ NOT DETECTED'}")
    print(f"   📦 LeRobot imports: {'✅ WORKING' if imports_ok else '❌ FAILED'}")
    
    if bi_manual_ready and imports_ok:
        print("🎉 System ready for bi-manual operation!")
    else:
        print("⚠️  System not ready - check issues above")
    
    return bi_manual_ready and imports_ok

if __name__ == "__main__":
    main()