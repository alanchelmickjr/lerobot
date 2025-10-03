# 🤖🤖 LeRobot Bi-Manual Upgrade Guide

**Transform your SO101 setup into a powerful bi-manual system with Joint, Independent & Mirror coordination modes!**

## 🎯 What You Get

### ✨ **Bi-Manual Coordination Modes**
- **🤝 COORDINATED**: Arms work together for complex dual-arm tasks
- **🆓 INDEPENDENT**: Each leader controls its own follower (left→left, right→right)
- **🪞 MIRROR**: Left leader controls BOTH arms, right follower mirrors left

### 🔍 **Auto-Detection Magic**
- Automatically detects 4-port bi-manual setups
- Voltage-based leader/follower identification
- Seamlessly switches between single and bi-manual modes

### 📱 **Touch-Friendly Interface** 
- Optimized for 7" touchscreens
- Big, clear buttons - no keyboard/mouse needed
- Perfect for Coofun Mini-PC setups

### 🚀 **Easy Updates**
- One-liner fork installation script
- Preserves your configurations
- Rollback support if needed

---

## 🚀 Quick Start

### For Touch Interface (7" Screen)
```bash
# Download and run (one command!)
curl -sSL https://raw.githubusercontent.com/YOUR-FORK/lerobot/main/update_lerobot_fork.sh | bash

# Launch touch UI
./start_lerobot_touch.sh
```

### For Terminal Interface
```bash
# Classic terminal UI with bimanual support
./start_lerobot_ui.sh
```

---

## 🔌 Hardware Setup

### Single SO101 Setup (2 ports)
```
Leader Arm (6-7V)  →  USB Port 1
Follower Arm (12V) →  USB Port 2
```

### Bi-Manual SO101 Setup (4 ports) 
```
Left Leader (6-7V)   →  USB Port 1
Left Follower (12V)  →  USB Port 2  
Right Leader (6-7V)  →  USB Port 3
Right Follower (12V) →  USB Port 4
```

**The system auto-detects which setup you have connected!**

---

## 🎮 Interface Options

### 1. 📱 Touch UI (`lerobot_touch_ui.py`)
**Perfect for 7" touchscreens**

- **Auto-Detection**: Instantly recognizes your setup
- **Mode Selection**: Big, clear buttons for coordination modes
- **Live Status**: Real-time rate and connection info
- **No Keyboard**: Pure touch control

**Launch with:**
```bash
./start_lerobot_touch.sh
```

### 2. 💻 Terminal UI (`lerobot_teleop_ui.py`) 
**Enhanced terminal interface**

- **Smart Detection**: Auto-switches between single and bi-manual
- **Mode Selection**: Interactive coordination mode picker
- **Diagnostics**: Motor health and voltage checking
- **Backwards Compatible**: All original features preserved

**Launch with:**
```bash
./start_lerobot_ui.sh
```

### 3. 🤖🤖 Standalone Bi-Manual (`lerobot_bimanual_ui.py`)
**Dedicated bi-manual interface**

- **4-Port Focus**: Designed specifically for bi-manual setups
- **Rich Interface**: Detailed mode descriptions and examples
- **Advanced Options**: Calibration, diagnostics, configuration

**Launch with:**
```bash
python lerobot_bimanual_ui.py
```

---

## 🤝 Coordination Modes Explained

### 🤝 COORDINATED Mode
**Status: Basic coordination implemented - suitable for simple tasks**

- Both leader arms control coordinated follower movement for basic dual-arm operations
- Suitable for simple pick-and-place and coordinated movements
- **Note**: Current implementation lacks advanced algorithms for genuine bimanual coordination, task-aware coordination, collision avoidance, and context-dependent strategies. These features are planned for future development.

**Example Use Cases:**
- Basic bimanual object manipulation
- Simple coordinated assembly tasks
- Two-handed demonstrations (basic)

### 🆓 INDEPENDENT Mode  
**Best for: Parallel tasks**

- Left leader → Left follower
- Right leader → Right follower
- Completely separate control systems
- Double productivity

**Example Use Cases:**
- Two operators working simultaneously
- Parallel assembly lines
- Independent task demonstration

### 🪞 MIRROR Mode
**Best for: Symmetrical operations**

- Left leader controls BOTH followers
- Right follower mirrors left follower exactly
- Single operator controls both arms
- Perfect symmetry guaranteed

**Example Use Cases:**
- Symmetrical assembly
- Demonstration recording
- Training scenarios

---

## 🔧 Installation & Updates

### Fresh Installation
```bash
# Clone the enhanced fork
git clone https://github.com/YOUR-FORK/lerobot.git
cd lerobot

# Run the touch launcher (handles everything)
./start_lerobot_touch.sh
```

### Update Existing Setup
```bash
# One-liner update (preserves your config)
curl -sSL https://raw.githubusercontent.com/YOUR-FORK/lerobot/main/update_lerobot_fork.sh | bash

# Or run locally
./update_lerobot_fork.sh
```

### What the Update Does
- ✅ Backs up your current setup
- ✅ Adds your fork as remote
- ✅ Switches to improvement branch
- ✅ Updates conda environment
- ✅ Preserves calibrations and settings

---

## 📋 File Overview

### Core Interface Files
- **`lerobot_touch_ui.py`** - Touch-optimized GUI (7" screens)
- **`lerobot_teleop_ui.py`** - Enhanced terminal UI 
- **`lerobot_bimanual_ui.py`** - Standalone bimanual interface

### Launcher Scripts  
- **`start_lerobot_touch.sh`** - Touch UI launcher
- **`start_lerobot_ui.sh`** - Terminal UI launcher (original enhanced)
- **`update_lerobot_fork.sh`** - One-liner fork updater

### Documentation
- **`BIMANUAL_UPGRADE_GUIDE.md`** - This comprehensive guide
- **`SO101_IMPROVEMENTS.md`** - Original improvements documentation

---

## 🔍 Troubleshooting

### "No 4-port setup detected"
- **Check connections**: Ensure all 4 USB cables are connected
- **Verify voltage**: Should have 2 low-voltage (6-7V) and 2 high-voltage (12V) arms
- **Port scanning**: Use diagnostics menu to check individual ports

### Touch UI won't start
- **Display check**: Ensure `DISPLAY` environment variable is set
- **Install tkinter**: `pip install tk` 
- **Fallback**: Use terminal UI instead: `./start_lerobot_ui.sh`

### Coordination modes not working
- **Check imports**: Ensure bi-manual classes are available
- **Calibration**: Try calibrating both arms first
- **Port assignment**: Verify correct leader/follower port mapping

### Fork update issues
- **Backup**: Your setup is automatically backed up before updates
- **Rollback**: `git checkout backup-YYYYMMDD-HHMMSS`
- **Clean install**: Delete and re-clone if needed

---

## 🎯 Performance Tips

### For Smooth Operation
- **USB 3.0**: Use USB 3.0 ports for better communication speed
- **Power supply**: Ensure adequate power for all 4 motors
- **Cable quality**: Use high-quality, short USB cables

### For Touch Interface
- **Screen calibration**: Calibrate touchscreen for accurate input
- **Resolution**: Optimized for 800x480, scales to other sizes
- **Fullscreen**: Press F11 for fullscreen mode

---

## 🚀 Next Steps

After getting bi-manual working, consider:

1. **LeKiwi Integration**: Mobile base + arm coordination
2. **XArm Support**: Industrial-grade arm integration  
3. **Custom Coordination**: Develop task-specific coordination algorithms
4. **Multi-Camera**: Enhanced vision with multiple camera feeds

---

## 💝 Credits

This bi-manual upgrade adds powerful coordination capabilities to the excellent LeRobot framework, making complex dual-arm robotics accessible to everyone!

**Key Features Delivered:**
- ✅ Joint/Independent/Mirror mode selection (as requested!)
- ✅ 4-port auto-detection  
- ✅ Touch-friendly interface for 7" screens
- ✅ One-liner fork deployment
- ✅ Backward compatibility with existing setups

**Happy bi-manual robotics! 🤖🤖**