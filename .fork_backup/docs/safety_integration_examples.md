# Motor Safety System - Automatic Protection

The motor safety system is now **automatically enabled by default** for all follower arms (SO100, SO101) to prevent servo damage during teleoperation, recording, and playback.

## How It Works

### Automatic Protection
When you run any LeRobot command with a follower arm, safety monitoring starts automatically:

```bash
# Teleoperation - Safety is ON automatically
lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem58760431551

# Recording - Safety is ON automatically  
lerobot-record \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --dataset.repo_id=user/my-dataset \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem58760431551

# Replay - Safety is ON automatically
lerobot-replay \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --dataset.repo_id=user/my-dataset \
    --dataset.episode=0
```

## What's Protected

### Temperature Protection
- **Warning at 40°C**: Logs warning, continues operation
- **Critical at 45°C**: Reduces torque by 50% automatically
- **Shutdown at 50°C**: Disables motor immediately

### Current Protection  
- **Stall Detection**: If current > 800mA for 0.5s, motor is disabled
- **Spike Protection**: If current > 1200mA, torque reduced immediately

### Mechanical Protection
- **Soft Start**: Smooth S-curve acceleration on all movements
- **Position Limits**: Automatic velocity reduction near joint limits

## Real-Time Monitoring

The safety system runs at 10Hz in the background, continuously checking:
- Motor temperatures
- Current draw
- Position limits
- Stall conditions

## Emergency Stop

If a critical condition is detected:
1. Affected motor is disabled immediately
2. Warning is logged to console
3. System continues operating other motors safely

## Disabling Safety (Not Recommended)

If you need to disable safety for testing:

```bash
# Disable safety monitoring (USE WITH CAUTION!)
lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --robot.enable_safety_monitoring=false \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem58760431551
```

## Custom Safety Thresholds

Adjust thresholds for your specific setup:

```bash
# More conservative temperature limits
lerobot-record \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem58760431541 \
    --robot.temperature_warning=35.0 \
    --robot.temperature_critical=40.0 \
    --robot.temperature_shutdown=45.0 \
    --robot.current_stall_threshold=600.0 \
    --dataset.repo_id=user/my-dataset
```

## Safety Logs

Monitor safety events in real-time:

```
[INFO] SO101Follower connected.
[INFO] Safety monitoring started
[WARNING] Temperature WARNING for shoulder_lift: 41.2°C
[WARNING] Safety event: temperature_warning for motor shoulder_lift with value 41.2
[INFO] Reduced torque for shoulder_lift to 512
[ERROR] Motor stall detected for elbow_flex: 850mA for 0.6s
[CRITICAL] EMERGENCY STOP - disabling all motors
```

## Benefits

✅ **Automatic Protection**: No manual configuration needed
✅ **Prevents Damage**: Stops motors before permanent damage occurs  
✅ **Extends Lifespan**: Soft start and torque management reduce wear
✅ **Peace of Mind**: Focus on your task, not motor health
✅ **Cost Savings**: No more burnt servos!

## Leader Arms

Leader arms (used for teleoperation) do **NOT** have safety monitoring enabled by default, as they:
- Experience less stress (human-controlled)
- Need full range for calibration procedures
- Are not driven by potentially erratic policy outputs

## Summary

The safety system is now an integral part of LeRobot's follower arm control. It runs transparently in the background, protecting your expensive servo motors from damage while maintaining smooth operation. 

**You don't need to do anything special - just use LeRobot normally and your motors are protected!**