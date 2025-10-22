# Fresh Installation Guide for LeRobot with SO101

## Prerequisites
- macOS or Linux system
- SO101 Leader and Follower arms
- USB-C cables for both arms

## Important: Miniconda vs Anaconda

**Choose ONE of these (not both):**

### Recommended: Miniconda (Lightweight ~400MB)
- ✅ **Best for LeRobot** - includes only conda + Python
- ✅ Faster installation and updates
- ✅ Less disk space
- ✅ Fewer potential conflicts

### Alternative: Anaconda (Full ~3GB)
- ⚠️ Includes 250+ data science packages you won't need for LeRobot
- ⚠️ Slower installation
- ⚠️ More disk space
- ✅ Good if you ALSO do data science work

**⚠️ WARNING**: Don't install both! They will conflict.

## Step 1: Clean Install of Conda

After running `cleanup_conda.sh` and rebooting, choose your installation:

### Option A: Miniconda (RECOMMENDED)

#### macOS (Apple Silicon M1/M2/M3):
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

#### macOS (Intel):
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
```

#### Linux (x86_64):
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

#### Linux (ARM64/aarch64 - Raspberry Pi, etc.):
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh
```

### Option B: Anaconda (Only if you need full data science stack)

#### macOS (Apple Silicon M1/M2/M3):
```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-MacOSX-arm64.sh
bash Anaconda3-2024.10-1-MacOSX-arm64.sh
```

#### macOS (Intel):
```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-MacOSX-x86_64.sh
bash Anaconda3-2024.10-1-MacOSX-x86_64.sh
```

#### Linux (x86_64):
```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
bash Anaconda3-2024.10-1-Linux-x86_64.sh
```

### During installation:
- Accept the license terms
- Use default location (~/miniconda3 or ~/anaconda3)
- Say YES to initialize conda

## Step 2: Restart Terminal

Close and reopen your terminal for conda to be available.

## Step 3: Create LeRobot Environment

```bash
# Create environment with Python 3.10
conda create -y -n lerobot python=3.10

# Activate the environment
conda activate lerobot

# Install ffmpeg
conda install ffmpeg -c conda-forge -y
```

## Step 4: Install LeRobot with Feetech Support

Navigate to your lerobot directory and install:

```bash
cd ~/dev/GitHub/lerobot  # or your lerobot directory
pip install -e ".[feetech]"

# Install pyserial for USB communication
pip install pyserial
```

## Step 5: Fix USB Permissions (if needed)

### macOS:
- USB devices should work without additional setup
- If issues occur, grant Terminal/VS Code access in System Preferences > Security & Privacy

### Linux:
```bash
# Add yourself to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again, or for immediate access:
sudo chmod 666 /dev/ttyUSB*
```

## Step 6: Run Auto-Calibration Script

With both SO101 arms connected:

```bash
python -m lerobot.scripts.auto_calibrate_so101
```

The script will:
1. Detect which port is leader vs follower
2. Calibrate the follower arm
3. Enable safety monitoring
4. Save configuration for future use

## Step 7: Test Teleoperation

After calibration, test with the detected ports:

```bash
lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=<FOLLOWER_PORT_FROM_CALIBRATION> \
    --teleop.type=so101_leader \
    --teleop.port=<LEADER_PORT_FROM_CALIBRATION>
```

## Safety Features

Your follower arm now has automatic protection:
- **Temperature monitoring**: Warns at 40°C, critical at 45°C, shutdown at 50°C
- **Current monitoring**: Detects stalls and prevents motor damage
- **Soft start**: Smooth acceleration to reduce wear
- **Position limits**: Prevents mechanical damage

Safety is enabled by default - no configuration needed!

## Troubleshooting

### Conda Issues
- If conda not found: Restart terminal or run `source ~/miniconda3/bin/activate`
- If permission errors: Check file ownership with `ls -la ~/.conda`

### USB Port Issues
- macOS: Check System Information > USB for connected devices
- Linux: Check `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
- Both: Try different USB ports or cables

### Motor Issues
- If motors don't respond: Check power supply
- If calibration fails: Ensure arms can move freely
- If safety triggers: Let motors cool down

## Resources

- [Miniconda Documentation](https://docs.conda.io/en/latest/miniconda.html)
- [LeRobot Documentation](https://github.com/huggingface/lerobot)
- [SO101 Robot Guide](https://github.com/TheRobotStudio/SO-ARM100)

---

Remember: The safety system is now protecting your motors automatically. Focus on your experiments, not on servo health!