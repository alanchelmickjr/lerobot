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
        """Detect bi-manual hardware setup"""
        ports = sorted(glob.glob('/dev/ttyACM*'))
        self.logger.info(f"Found {len(ports)} ACM ports: {ports}")
        
        if len(ports) == 4:
            return {
                'status': 'bi_manual',
                'ports': ports,
                'mapping': {
                    'left_leader': ports[0],    # ACM0
                    'right_leader': ports[1],   # ACM1  
                    'left_follower': ports[2],  # ACM2
                    'right_follower': ports[3]  # ACM3
                }
            }
        elif len(ports) == 2:
            return {
                'status': 'single_arm',
                'ports': ports,
                'mapping': {
                    'leader': ports[0],
                    'follower': ports[1]
                }
            }
        else:
            return {'status': 'no_robots', 'ports': ports, 'mapping': {}}
    
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