#!/usr/bin/env python3
"""
Simple test for INDEPENDENT bi-manual mode
No GUI - just direct robot control
"""
import sys
import time
from pathlib import Path

# Add lerobot to path
lerobot_path = Path('/home/feetech/lerobot/src')
if lerobot_path.exists() and str(lerobot_path) not in sys.path:
    sys.path.insert(0, str(lerobot_path))

try:
    from bimanual_api import BiManualAPI
    from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
    from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_independent_mode():
    """Test INDEPENDENT mode: 2 leaders → 2 followers"""
    print("🚀 Testing INDEPENDENT Bi-Manual Mode")
    print("=" * 50)
    
    # Get system status
    api = BiManualAPI()
    status = api.get_system_status()
    
    if not status['ready']:
        print("❌ System not ready!")
        return False
    
    ports = status['hardware']['mapping']
    print(f"📍 Port mapping:")
    for name, port in ports.items():
        print(f"   {name}: {port}")
    
    try:
        # Create INDEPENDENT configs (both leaders active)
        print("\n🔗 Creating robot configs...")
        robot_config = BiSO100FollowerConfig(
            left_arm_port=ports['left_follower'],    # ACM2
            right_arm_port=ports['right_follower'],  # ACM3
            id="bimanual_follower"
        )
        
        teleop_config = BiSO100LeaderConfig(
            left_arm_port=ports['left_leader'],     # ACM0
            right_arm_port=ports['right_leader'],   # ACM1
            id="bimanual_leader"
        )
        
        print("🤖 Connecting to followers...")
        robot = BiSO100Follower(robot_config)
        robot.connect()
        
        print("🎮 Connecting to leaders...")
        teleop = BiSO100Leader(teleop_config)
        teleop.connect()
        
        print("\n✅ INDEPENDENT MODE ACTIVE!")
        print("🎯 Move BOTH leader arms:")
        print("   Left leader (ACM0) → Left follower (ACM2)")
        print("   Right leader (ACM1) → Right follower (ACM3)")
        print("\nPress Ctrl+C to stop...")
        
        # Control loop
        loop_count = 0
        start_time = time.time()
        
        while True:
            try:
                # Get action from BOTH leaders
                action = teleop.get_action()
                
                # Send to BOTH followers
                robot.send_action(action)
                
                # Status every 200 loops
                loop_count += 1
                if loop_count % 200 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed if elapsed > 0 else 0
                    print(f"\r📊 Rate: {rate:.1f} Hz | Loops: {loop_count:>4} | Time: {elapsed:.1f}s", end="", flush=True)
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Stopping...")
                break
            except Exception as e:
                print(f"\n❌ Control error: {e}")
                break
        
        # Cleanup
        print("🔌 Disconnecting...")
        robot.disconnect()
        teleop.disconnect()
        print("✅ Test complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_independent_mode()
    if success:
        print("\n🎉 INDEPENDENT mode working!")
    else:
        print("\n💥 INDEPENDENT mode failed!")