#!/usr/bin/env python3
"""
Bi-Manual Robot Detection & Control API
Small, simple, elegant - core logic separated from GUI
"""
import glob
import logging
import sys
from pathlib import Path

class BiManualAPI:
    """Clean API for bi-manual robot detection and control"""
    
    def __init__(self, log_level=logging.INFO):
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
        
    def detect_hardware(self):
        """Detect scalable robot hardware setup (single, bi, tri, quad-manual)"""
        ports = sorted(glob.glob('/dev/ttyACM*'))
        num_ports = len(ports)
        self.logger.info(f"Found {num_ports} ACM ports: {ports}")
        
        # Scalable detection based on port pairs (even numbers = leader+follower pairs)
        if num_ports == 2:
            return {
                'status': 'single_arm',
                'arm_count': 1,
                'ports': ports,
                'mapping': {
                    'leader': ports[0],      # ACM0
                    'follower': ports[1]     # ACM1
                }
            }
        elif num_ports == 4:
            return {
                'status': 'bi_manual',
                'arm_count': 2,
                'ports': ports,
                'mapping': {
                    'left_leader': ports[0],    # ACM0
                    'right_leader': ports[1],   # ACM1
                    'left_follower': ports[2],  # ACM2
                    'right_follower': ports[3]  # ACM3
                }
            }
        elif num_ports == 6:
            return {
                'status': 'tri_manual',
                'arm_count': 3,
                'ports': ports,
                'mapping': {
                    'leader_1': ports[0],    # ACM0
                    'leader_2': ports[1],    # ACM1
                    'leader_3': ports[2],    # ACM2
                    'follower_1': ports[3],  # ACM3
                    'follower_2': ports[4],  # ACM4
                    'follower_3': ports[5]   # ACM5
                }
            }
        elif num_ports == 8:
            return {
                'status': 'quad_manual',
                'arm_count': 4,
                'ports': ports,
                'mapping': {
                    'leader_1': ports[0],    # ACM0
                    'leader_2': ports[1],    # ACM1
                    'leader_3': ports[2],    # ACM2
                    'leader_4': ports[3],    # ACM3
                    'follower_1': ports[4],  # ACM4
                    'follower_2': ports[5],  # ACM5
                    'follower_3': ports[6],  # ACM6
                    'follower_4': ports[7]   # ACM7
                }
            }
        elif num_ports > 0 and num_ports % 2 == 0:
            # Generic even number support
            num_pairs = num_ports // 2
            mapping = {}
            for i in range(num_pairs):
                mapping[f'leader_{i+1}'] = ports[i]
                mapping[f'follower_{i+1}'] = ports[i + num_pairs]
            
            return {
                'status': f'{num_pairs}_manual',
                'arm_count': num_pairs,
                'ports': ports,
                'mapping': mapping
            }
        else:
            return {
                'status': 'unsupported' if num_ports > 0 else 'no_robots',
                'arm_count': 0,
                'ports': ports,
                'mapping': {}
            }
    
    def test_imports(self):
        """Test LeRobot imports"""
        try:
            # Add lerobot to path if needed
            lerobot_path = Path('/home/feetech/lerobot/src')
            if lerobot_path.exists() and str(lerobot_path) not in sys.path:
                sys.path.insert(0, str(lerobot_path))
            
            from lerobot.robots.bi_so100_follower import BiSO100Follower
            from lerobot.teleoperators.bi_so100_leader import BiSO100Leader
            self.logger.info("✅ LeRobot imports successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ Import failed: {e}")
            return False
    
    def get_system_status(self):
        """Get complete system status"""
        hardware = self.detect_hardware()
        imports_ok = self.test_imports()
        
        return {
            'hardware': hardware,
            'imports_ok': imports_ok,
            'ready': hardware['status'] == 'bi_manual' and imports_ok
        }

def main():
    """Simple CLI test"""
    api = BiManualAPI()
    status = api.get_system_status()
    
    print("🚀 Bi-Manual API Test")
    print(f"Hardware: {status['hardware']['status']}")
    print(f"Imports: {'✅' if status['imports_ok'] else '❌'}")
    print(f"Ready: {'🎉 YES' if status['ready'] else '❌ NO'}")
    
    return status['ready']

if __name__ == "__main__":
    main()