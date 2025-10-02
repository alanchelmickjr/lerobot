#!/usr/bin/env python3
"""
SSH Dependencies Installation Script
Handles sshpass installation and verification for SSH auto-login
"""

import subprocess
import shutil
import sys
import os

def check_sshpass():
    """Check if sshpass is available"""
    return shutil.which("sshpass") is not None

def install_sshpass_ubuntu():
    """Install sshpass on Ubuntu/Debian systems"""
    try:
        print("🔧 Installing sshpass on Ubuntu/Debian...")
        result = subprocess.run([
            "sudo", "apt-get", "update", "&&", 
            "sudo", "apt-get", "install", "-y", "sshpass"
        ], shell=True, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ sshpass installed successfully")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def install_sshpass_macos():
    """Install sshpass on macOS using Homebrew"""
    try:
        print("🔧 Installing sshpass on macOS...")
        # First check if Homebrew is available
        if not shutil.which("brew"):
            print("❌ Homebrew not found. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
        
        result = subprocess.run([
            "brew", "install", "hudochenkov/sshpass/sshpass"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ sshpass installed successfully via Homebrew")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def main():
    """Main dependency checker and installer"""
    print("🔍 Checking SSH dependencies...")
    
    if check_sshpass():
        print("✅ sshpass is already installed")
        return True
    
    print("⚠️  sshpass not found - required for SSH auto-login")
    
    # Detect OS and suggest installation
    if sys.platform.startswith('linux'):
        if os.path.exists('/etc/debian_version'):
            print("📋 Detected Ubuntu/Debian system")
            install_sshpass_ubuntu()
        else:
            print("📋 Detected Linux system")
            print("Please install sshpass using your package manager:")
            print("  - Ubuntu/Debian: sudo apt-get install sshpass")
            print("  - Red Hat/CentOS: sudo yum install sshpass")
            print("  - Arch: sudo pacman -S sshpass")
    
    elif sys.platform == 'darwin':
        print("📋 Detected macOS system")
        install_sshpass_macos()
    
    else:
        print("📋 Unsupported system for automatic installation")
        print("Please install sshpass manually for your system")
    
    # Verify installation
    if check_sshpass():
        print("🎉 SSH dependencies are ready!")
        return True
    else:
        print("❌ sshpass installation incomplete")
        print("SSH auto-login functionality will not work without sshpass")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)