# Collision Detection and Intelligent Recovery System

## Overview

The SO-101 robot arm now features an advanced collision detection system that protects both the robot and its environment. When the arm encounters an obstacle, it intelligently backs off, retries with caution, and can trigger auto-recalibration when needed.

## Key Features

### 1. **Intelligent Collision Detection**
- **Current Monitoring**: Detects motor stalls when current exceeds 900mA
- **Torque Sensing**: Monitors normalized torque (threshold: 0.3)
- **Duration Filtering**: Requires 0.3 seconds of sustained force to confirm collision
- **False Positive Prevention**: Filters out brief spikes and normal operation variance

### 2. **Smart Backoff Strategy**
When a collision is detected:
1. **Immediate Stop**: Halts forward movement
2. **Calculated Backoff**: Moves back 0.1 normalized units (configurable)
3. **Cooldown Period**: Waits 2 seconds before retry
4. **Retry Logic**: Attempts up to 3 times before aborting
5. **No Bouncing**: Prevents repeated hits on the same obstacle

### 3. **Auto-Recalibration Triggers**
The system automatically triggers recalibration when:
- **Collision Count**: 5+ collisions detected
- **Time-Based**: 1+ hours since last calibration
- **Position Errors**: Repeated collisions at same position (indicates calibration drift)
- **Limit Violations**: Unexpected operational limit exceeded

### 4. **Adaptive Performance Monitoring**
The system continuously optimizes its monitoring frequency based on:
- **Smoothness Score**: Tracks movement jitter (0-1 scale)
- **Processing Latency**: Measures loop execution time
- **CPU Load**: Adjusts to system capabilities
- **Dynamic Frequency**: Ranges from 0.5Hz to 10Hz based on conditions

## Configuration

Add these settings to your `config_so101_follower.py`:

```python
# Collision detection configuration
enable_collision_detection: bool = True
collision_torque_threshold: float = 0.3  # Normalized torque (0-1)
collision_current_threshold: float = 900.0  # mA
collision_duration: float = 0.3  # seconds
collision_backoff_distance: float = 0.1  # Normalized units
collision_max_retries: int = 3  # Max attempts

# Auto-recalibration triggers
auto_recalibrate_on_collisions: int = 5
auto_recalibrate_time_hours: float = 1.0
```

## Usage Examples

### Basic Usage with Collision Detection

```python
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# Configure with collision detection
config = SO101FollowerConfig(
    port="/dev/ttyUSB0",
    enable_collision_detection=True,
    collision_current_threshold=800.0,  # More sensitive
    collision_max_retries=5  # More retries
)

robot = SO101Follower(config)
robot.connect()

# Movement automatically includes collision detection
action = {"shoulder_pan.pos": 0.5, "elbow_flex.pos": 0.3}
result = robot.send_action(action)

# The robot will automatically:
# - Detect collisions
# - Back off when hitting obstacles
# - Retry movement
# - Trigger recalibration if needed
```

### Monitoring Collision Events

```python
# Get safety status including collision metrics
status = robot.get_safety_status()

print(f"Total collisions: {status['collision_detection']['total_collisions']}")
print(f"Movement smoothness: {status['collision_detection']['smoothness']:.2f}")
print(f"Monitoring frequency: {status['collision_detection']['monitoring_freq']:.1f}Hz")
```

### Manual Collision Handling

```python
from lerobot.motors.collision_detection import SmartCollisionSafetySystem

# Use the collision system directly
collision_system = robot.collision_system

# Execute movement with collision detection
goal_positions = {"shoulder_pan": 0.5, "elbow_flex": 0.3}
result = collision_system.safe_move_with_collision_detection(
    goal_positions,
    timeout=5.0
)

# Check results
if result['success']:
    print("Movement completed successfully")
else:
    for motor, collision_info in result['collisions'].items():
        print(f"Collision on {motor}: {collision_info}")
        
if result['recalibration_triggered']:
    print("Auto-recalibration was triggered")
```

## Performance Metrics

### Smoothness Score
- **1.0**: Perfect smooth movement
- **0.7-0.9**: Good, normal operation
- **0.5-0.7**: Acceptable, minor jitter
- **<0.5**: Poor, significant jitter (frequency will increase)

### Adaptive Frequency
The monitoring frequency automatically adjusts:
- **High smoothness + Low latency**: Maintains current frequency
- **Low smoothness + Low latency**: Increases frequency (up to 10Hz)
- **High smoothness + High latency**: Decreases frequency (down to 0.5Hz)
- **Very high latency (>100ms)**: Aggressively reduces frequency

## Safety Behavior

### Hand Blocking Test
When you place your hand in the robot's path:
1. Robot detects increased current/torque
2. After 0.3 seconds of resistance, triggers collision
3. Backs off 0.1 units
4. Waits 2 seconds (cooldown)
5. Retries movement (up to 3 times)
6. If hand remains, aborts movement
7. No damage to hand or robot!

### Wall Contact
When the arm hits a wall:
1. Immediate detection via current spike
2. Backs away from wall
3. Attempts alternative approach
4. Triggers recalibration if position limits exceeded
5. Prevents motor damage from sustained stall

## Troubleshooting

### Issue: Too Sensitive (False Positives)
Increase thresholds:
```python
collision_current_threshold: float = 1000.0  # Higher threshold
collision_duration: float = 0.5  # Longer confirmation time
```

### Issue: Not Detecting Collisions
Decrease thresholds:
```python
collision_current_threshold: float = 700.0  # Lower threshold
collision_torque_threshold: float = 0.2  # More sensitive
```

### Issue: Movement Too Jerky
Check adaptive frequency:
```python
status = robot.get_safety_status()
freq = status['collision_detection']['monitoring_freq']
if freq > 5.0:
    # System is trying to compensate for poor smoothness
    # Check mechanical issues or reduce load
```

### Issue: Repeated Collisions Same Position
This triggers auto-recalibration. If it persists:
1. Check for mechanical obstruction
2. Verify motor mounting
3. Inspect wiring for intermittent connections
4. Consider manual recalibration

## Integration with Motor Safety

The collision detection works seamlessly with the motor safety system:
- **Temperature Protection**: Still active during collisions
- **Emergency Stop**: Overrides collision recovery
- **Soft Start**: Applied after backoff movements
- **Current Monitoring**: Shared between systems

## Best Practices

1. **Test Sensitivity**: Start with default settings, adjust based on your application
2. **Monitor Metrics**: Check smoothness scores regularly
3. **Regular Calibration**: Even with auto-recalibration, monthly manual checks recommended
4. **Log Collisions**: Track collision events to identify problem areas
5. **Gradual Movements**: Slower movements give better collision detection

## API Reference

### CollisionConfig
```python
@dataclass
class CollisionConfig:
    torque_threshold: float = 0.3
    current_threshold: float = 900.0
    collision_duration: float = 0.3
    backoff_distance: float = 0.1
    backoff_speed: float = 0.5
    cooldown_period: float = 2.0
    max_retries: int = 3
    position_error_threshold: float = 0.05
    consecutive_collisions_for_recal: int = 5
    time_since_last_calibration: float = 3600.0
```

### CollisionDetector Methods
- `detect_collision()`: Check for collision on specific motor
- `trigger_recalibration()`: Manually trigger recalibration
- `update_smoothness_metrics()`: Update performance metrics
- `get_adaptive_frequency()`: Get current optimal monitoring frequency

### SmartCollisionSafetySystem Methods
- `safe_move_with_collision_detection()`: Execute movement with collision handling
- `_trigger_recalibration()`: Internal recalibration handler

## Future Enhancements

Planned improvements:
- Machine learning for collision prediction
- Vision-based obstacle detection
- Force feedback integration
- Collaborative mode for human interaction
- Path planning around detected obstacles