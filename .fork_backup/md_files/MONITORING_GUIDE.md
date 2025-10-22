# 🔍 Bi-Manual System Monitoring Guide

## Quick Commands (SSH to Coofun)

```bash
# Connect to Coofun
ssh feetech@192.168.88.22
cd ~/lerobot
source ~/miniconda3/bin/activate
conda activate lerobot
```

## System Status Check
```bash
# Quick health check
python3 monitor_bimanual.py

# Expected output:
# 🤖 Hardware: bi_manual  
# 📦 Imports: ✅
# 🎯 Ready: 🎉 YES
```

## Real-Time Monitoring  
```bash
# Watch live logs
python3 monitor_bimanual.py logs

# Test core API only
python3 bimanual_api.py
```

## Port Mapping (Your Setup)
- **ACM0**: Left Leader
- **ACM1**: Right Leader  
- **ACM2**: Left Follower
- **ACM3**: Right Follower

## Touch Interface Usage
1. **Touch desktop icon**: "Bi-Manual Robot Control"
2. **See mode selection**:
   - 🤝 **COORDINATED** (Green) - Basic coordinated movement for simple tasks
   - 🆓 **INDEPENDENT** (Blue) - Left→Left, Right→Right (fully implemented)
   - 🪞 **MIRROR** (Purple) - Left controls both (fully implemented)

## Architecture
```
bimanual_api.py     ← Core logic (API)
     ↕
simple_touch_ui.py  ← Thin GUI layer
     ↕
Desktop Icon        ← Touch interface
```

## Troubleshooting
- **No display error**: Normal via SSH, use desktop icon
- **Import errors**: Check conda environment activation
- **Port issues**: Run `ls /dev/ttyACM*` to verify 4 ports
- **GUI freezes**: Check `python3 monitor_bimanual.py logs`

## Files Deployed
- `/home/feetech/lerobot/bimanual_api.py` - Core API
- `/home/feetech/lerobot/simple_touch_ui.py` - Touch GUI
- `/home/feetech/lerobot/monitor_bimanual.py` - Monitoring tools  
- `/home/feetech/Desktop/BiManual-Robot-Control.desktop` - Touch launcher