#!/usr/bin/env python3
"""
ML Camera Detective - Identify that mystery camera! 📷🕵️
Run this when you're done testing robot modes
"""
import subprocess
import re
import os
from pathlib import Path

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def detect_usb_cameras():
    """Detect USB cameras"""
    print("📷 USB CAMERA DETECTION")
    print("=" * 50)
    
    # Get all USB devices
    lsusb_output = run_command("lsusb")
    print("🔍 All USB devices:")
    print(lsusb_output)
    print()
    
    # Filter for camera-like devices
    camera_keywords = [
        'camera', 'video', 'imaging', 'webcam', 'cam', 'vision',
        'realsense', 'oak', 'zed', 'logitech', 'microsoft', 'sony',
        'intel', 'luxonis', 'stereolabs', 'asus'
    ]
    
    print("🎯 Potential Camera Devices:")
    camera_devices = []
    
    for line in lsusb_output.split('\n'):
        for keyword in camera_keywords:
            if keyword.lower() in line.lower():
                print(f"   📷 {line}")
                camera_devices.append(line)
                break
    
    if not camera_devices:
        print("   ❌ No obvious camera devices found in lsusb")
    
    return camera_devices

def detect_video_devices():
    """Detect /dev/video* devices"""
    print("\n📂 VIDEO DEVICE DETECTION")  
    print("=" * 50)
    
    video_devices = []
    video_path = Path("/dev")
    
    # Find /dev/video* devices
    for device in video_path.glob("video*"):
        video_devices.append(str(device))
    
    if video_devices:
        print("🎥 Found video devices:")
        for device in sorted(video_devices):
            print(f"   📹 {device}")
            
            # Get device info using v4l2-ctl if available
            info_cmd = f"v4l2-ctl --device={device} --info 2>/dev/null || echo 'v4l2-ctl not available'"
            info = run_command(info_cmd)
            if "v4l2-ctl not available" not in info:
                print(f"      ℹ️  {info}")
    else:
        print("❌ No /dev/video* devices found")
    
    return video_devices

def check_camera_software():
    """Check for camera-related software"""
    print("\n🛠️ CAMERA SOFTWARE DETECTION")
    print("=" * 50)
    
    software_checks = {
        "v4l-utils": "v4l2-ctl --version",
        "OpenCV": "python3 -c 'import cv2; print(f\"OpenCV {cv2.__version__}\")'",
        "RealSense SDK": "python3 -c 'import pyrealsense2 as rs; print(\"RealSense SDK installed\")'",
        "Luxonis DepthAI": "python3 -c 'import depthai as dai; print(\"DepthAI SDK installed\")'",
    }
    
    for name, cmd in software_checks.items():
        result = run_command(cmd)
        if "not found" in result.lower() or "error" in result.lower():
            print(f"   ❌ {name}: Not installed")
        else:
            print(f"   ✅ {name}: {result}")

def identify_camera_model():
    """Try to identify specific camera models"""
    print("\n🔍 CAMERA MODEL IDENTIFICATION")
    print("=" * 50)
    
    # Common ML camera USB IDs
    known_cameras = {
        "8086:0b03": "Intel RealSense D415/D435",
        "8086:0af6": "Intel RealSense D455", 
        "8086:0b07": "Intel RealSense D405",
        "03e7:2485": "Luxonis OAK-D",
        "03e7:f63b": "Luxonis OAK-D Pro",
        "2b03:f580": "Luxonis OAK-1", 
        "0b05:4845": "ASUS Xtion Pro Live",
        "1d27:0600": "ORBBEC Astra series",
        "2bc5:0401": "Stereolabs ZED",
        "046d:085b": "Logitech C920 HD Pro",
        "046d:082d": "Logitech HD Pro C920",
    }
    
    lsusb_output = run_command("lsusb")
    
    found_known = False
    for usb_id, camera_name in known_cameras.items():
        if usb_id.lower() in lsusb_output.lower():
            print(f"🎯 IDENTIFIED: {camera_name}")
            print(f"   USB ID: {usb_id}")
            found_known = True
    
    if not found_known:
        print("❓ Camera model not in database")
        print("   Check the USB vendor/device IDs above against:")
        print("   - Intel RealSense: 8086:****")
        print("   - Luxonis OAK: 03e7:****") 
        print("   - Logitech: 046d:****")
        print("   - Stereolabs ZED: 2bc5:****")

def detect_ml_features():
    """Detect ML/AI specific camera features"""
    print("\n🤖 ML/AI CAMERA FEATURES")
    print("=" * 50)
    
    features_to_check = [
        ("Depth sensing", "ls /dev/*depth* 2>/dev/null || echo 'No depth devices'"),
        ("Infrared cameras", "ls /dev/video* 2>/dev/null | wc -l"),  
        ("IMU sensors", "ls /dev/imu* /dev/*imu* 2>/dev/null || echo 'No IMU devices'"),
        ("AI accelerator", "lspci | grep -i 'neural\\|ai\\|movidius' || echo 'No AI accelerator'"),
    ]
    
    for feature_name, cmd in features_to_check:
        result = run_command(cmd)
        print(f"   {feature_name}: {result}")

def main():
    """Main camera detection function"""
    print("🎬 MYSTERY ML CAMERA DETECTIVE 🕵️")
    print("=" * 60)
    print("Investigating the camera that arrived in one of those boxes...")
    print()
    
    # Run all detection methods
    usb_cameras = detect_usb_cameras()
    video_devices = detect_video_devices()
    check_camera_software()
    identify_camera_model()
    detect_ml_features()
    
    # Summary
    print("\n📋 INVESTIGATION SUMMARY")
    print("=" * 50)
    
    if usb_cameras:
        print("✅ Camera hardware detected via USB")
    else:
        print("❌ No camera hardware detected")
        
    if video_devices:
        print(f"✅ {len(video_devices)} video device(s) available")
    else:
        print("❌ No video devices available")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Share this output to identify the camera model")
    print("   2. Install appropriate SDK if needed")  
    print("   3. Test camera with: 'python3 -c \"import cv2; cap=cv2.VideoCapture(0); print('Camera works!' if cap.isOpened() else 'Camera failed')'\"")
    print("   4. Add camera to LeRobot bi-manual setup for vision")

if __name__ == "__main__":
    main()