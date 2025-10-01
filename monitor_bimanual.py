#!/usr/bin/env python3
"""
Simple monitoring tool for bi-manual system
Real-time logs and status monitoring
"""
import subprocess
import time
import sys
from pathlib import Path

def tail_logs():
    """Tail application logs"""
    log_file = Path("/home/feetech/lerobot/bimanual.log")
    
    if not log_file.exists():
        print("📝 No log file yet, starting fresh...")
        log_file.touch()
    
    print("🔍 Monitoring bi-manual system logs...")
    print("=" * 50)
    
    try:
        # Use subprocess to tail the log file
        process = subprocess.Popen(['tail', '-f', str(log_file)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output:
                print(f"📊 {time.strftime('%H:%M:%S')} | {output.strip()}")
            time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
        process.terminate()

def check_status():
    """Quick status check"""
    print("🚀 BI-MANUAL SYSTEM STATUS")
    print("=" * 30)
    
    # Check API
    try:
        from bimanual_api import BiManualAPI
        api = BiManualAPI()
        status = api.get_system_status()
        
        print(f"🤖 Hardware: {status['hardware']['status']}")
        print(f"📦 Imports: {'✅' if status['imports_ok'] else '❌'}")
        print(f"🎯 Ready: {'🎉 YES' if status['ready'] else '❌ NO'}")
        
        if status['hardware']['status'] == 'bi_manual':
            mapping = status['hardware']['mapping']
            print("\n🔌 PORT MAPPING:")
            for name, port in mapping.items():
                print(f"   {name}: {port}")
                
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'logs':
        tail_logs()
    else:
        check_status()

if __name__ == "__main__":
    main()