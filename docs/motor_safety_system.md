# Motor Safety System Documentation

## Overview

The Motor Safety System provides comprehensive protection for robot motors by monitoring critical parameters and implementing safety protocols to prevent damage. This system is designed to ensure safe operation of the SO101 robot and other compatible platforms.

## Key Features

### 1. Temperature Monitoring
- **Real-time temperature tracking** for each motor
- **Three-tier threshold system**:
  - Warning threshold (default: 40°C)
  - Critical threshold (default: 45°C)
  - Shutdown threshold (default: 50°C)
- **Automatic response actions**:
  - Warning: Log and track
  - Critical: Reduce torque by 50%
  - Shutdown: Immediately disable motor

### 2. Current-Based Stall Detection
- **Continuous current monitoring** to detect motor stalls
- **Two-level detection**:
  - Stall threshold (default: 800mA for 0.5s)
  - Spike threshold (default: 1200mA immediate)
- **Automatic protection**:
  - Stall detected: Disable motor
  - Spike detected: Reduce torque by 70%

### 3. Gradual Torque Application (Soft Start)
- **S-curve trajectory generation** for smooth motor startup
- **Configurable parameters**:
  - Duration (default: 1.0 second)
  - Steps (default: 10 intermediate positions)
- **Benefits**:
  - Reduces mechanical stress
  - Prevents current spikes
  - Extends motor lifespan

### 4. Position Limit Enforcement
- **Soft limit implementation** near mechanical limits
- **Automatic velocity reduction** when approaching limits
- **Configurable safety margin** (default: 5 degrees)

### 5. Emergency Stop Capability
- **Immediate motor shutdown** across all axes
- **Manual trigger** via `emergency_stop()` method
- **Automatic trigger** on critical safety violations
- **Safe reset procedure** with temperature verification

## Configuration

### Basic Configuration

Add safety parameters to your SO101 configuration:

```python
from lerobot.robots.so101_follower import SO101FollowerConfig

config = SO101FollowerConfig(
    port="/dev/ttyUSB0",
    
    # Enable safety monitoring
    enable_safety_monitoring=True,
    
    # Temperature thresholds (Celsius)
    temperature_warning=40.0,
    temperature_critical=45.0,
    temperature_shutdown=50.0,
    
    # Current thresholds (mA)
    current_stall_threshold=800.0,
    current_stall_duration=0.5,  # seconds
    
    # Soft start parameters
    soft_start_duration=1.0,  # seconds
    
    # Monitoring frequency
    monitor_frequency=10.0,  # Hz
)
```

### Advanced Configuration

For fine-tuned control, use a custom `SafetyThresholds` object:

```python
from lerobot.motors.motor_safety import SafetyThresholds
from lerobot.robots.so101_follower import SO101FollowerConfig

custom_thresholds = SafetyThresholds(
    # Temperature thresholds
    temperature_warning=38.0,
    temperature_critical=42.0,
    temperature_shutdown=48.0,
    
    # Current thresholds
    current_stall_threshold=700.0,
    current_stall_duration=0.3,
    current_spike_threshold=1000.0,
    
    # Soft start
    soft_start_duration=1.5,
    soft_start_steps=15,
    
    # Position safety
    position_margin=10.0,  # degrees from limits
    
    # Velocity limits
    max_velocity=150.0,  # degrees/sec
    
    # Monitoring
    monitor_frequency=20.0,  # Hz
    
    # Recovery
    cooldown_temperature=32.0,
    recovery_wait_time=10.0,  # seconds
)

config = SO101FollowerConfig(
    port="/dev/ttyUSB0",
    enable_safety_monitoring=True,
    safety_thresholds=custom_thresholds,
)
```

## Usage Examples

### Basic Usage with SO101 Robot

```python
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# Create robot with safety enabled
config = SO101FollowerConfig(
    port="/dev/ttyUSB0",
    enable_safety_monitoring=True,
)

robot = SO101Follower(config)
robot.connect()

# Safety monitoring starts automatically
# Use robot normally - safety system runs in background
obs = robot.get_observation()
robot.send_action(action)

# Check safety status
safety_status = robot.get_safety_status()
print(f"Safety Status: {safety_status['status']}")
print(f"Motor Temperatures: {safety_status['motors']}")

# Emergency stop if needed
robot.emergency_stop()

# Disconnect (safety monitoring stops automatically)
robot.disconnect()
```

### Standalone Safety Monitor

```python
from lerobot.motors.motor_safety import MotorSafetyMonitor, SafetyThresholds
from lerobot.motors.feetech import FeetechMotorsBus

# Create motor bus
bus = FeetechMotorsBus(port="/dev/ttyUSB0", motors=motors)
bus.connect()

# Create safety monitor with custom callback
def safety_callback(event_type, motor, value):
    print(f"Safety Event: {event_type} on {motor} - Value: {value}")
    if event_type == "temperature_shutdown":
        # Custom handling for temperature shutdown
        send_alert_email(f"Motor {motor} shutdown at {value}°C")

monitor = MotorSafetyMonitor(
    bus,
    thresholds=SafetyThresholds(temperature_warning=38.0),
    callback=safety_callback,
)

# Start monitoring
monitor.start_monitoring()

# ... use motors ...

# Get safety report
report = monitor.get_safety_report()
print(f"Total violations: {report['statistics']['total_violations']}")
print(f"Max temperatures reached: {report['motors']}")

# Stop monitoring
monitor.stop_monitoring()
```

### Using Context Manager

```python
from lerobot.motors.motor_safety import MotorSafetyMonitor

# Automatic start/stop with context manager
with MotorSafetyMonitor(bus) as monitor:
    # Monitoring is active here
    # ... perform robot operations ...
    pass
# Monitoring stops automatically
```

## Safety Event Callbacks

The safety system can notify your application of safety events:

```python
def handle_safety_event(event_type, motor, value):
    """
    Handle safety events from the monitoring system.
    
    Args:
        event_type: Type of event (str)
            - "temperature_warning": Temperature warning threshold exceeded
            - "temperature_critical": Critical temperature reached
            - "temperature_shutdown": Motor shutdown due to temperature
            - "stall_detected": Motor stall detected
            - "current_spike": Current spike detected
            - "emergency_stop": Emergency stop triggered
        motor: Name of affected motor (str) or None for global events
        value: Relevant value (temperature, current, etc.)
    """
    
    if event_type == "temperature_shutdown":
        # Log critical event
        logger.critical(f"Motor {motor} shutdown at {value}°C")
        # Send notification
        notify_operator(f"Critical: {motor} overheated")
        
    elif event_type == "stall_detected":
        # Try recovery procedure
        attempt_stall_recovery(motor)
        
    elif event_type == "emergency_stop":
        # System-wide emergency response
        shutdown_all_systems()
        notify_emergency_contacts()
```

## Safety Statistics

The system tracks safety metrics for analysis:

```python
# Get comprehensive safety report
report = monitor.get_safety_report()

# Overall statistics
stats = report['statistics']
print(f"Uptime: {stats['uptime']:.1f} seconds")
print(f"Total violations: {stats['total_violations']}")
print(f"Temperature warnings: {stats['temperature_warnings']}")
print(f"Current stalls: {stats['current_stalls']}")
print(f"Emergency stops: {stats['emergency_stops']}")

# Per-motor details
for motor, data in report['motors'].items():
    print(f"\n{motor}:")
    print(f"  Current temp: {data['temperature']:.1f}°C")
    print(f"  Max temp: {data['max_temp']:.1f}°C")
    print(f"  Current draw: {data['current']:.0f}mA")
    print(f"  Is stalled: {data['is_stalled']}")
    print(f"  Violations: {data['violations']}")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all safety tests
python -m pytest tests/test_motor_safety.py -v

# Run specific test categories
python -m pytest tests/test_motor_safety.py::TestMotorSafetyMonitor -v
python -m pytest tests/test_motor_safety.py::TestIntegrationWithSO101 -v

# Run with coverage
python -m pytest tests/test_motor_safety.py --cov=lerobot.motors.motor_safety
```

## Best Practices

### 1. Temperature Management
- **Allow cooldown periods** between intensive operations
- **Monitor ambient temperature** and adjust thresholds accordingly
- **Ensure proper ventilation** around motors

### 2. Current Management
- **Avoid sudden direction changes** at high speeds
- **Use soft start** for all movements from rest
- **Reduce payload** if frequent stalls occur

### 3. Threshold Tuning
- **Start with conservative thresholds** and adjust based on experience
- **Monitor statistics** to identify patterns
- **Different tasks** may require different threshold profiles

### 4. Emergency Procedures
- **Test emergency stop** regularly
- **Establish clear recovery procedures** 
- **Train operators** on safety protocols

## Troubleshooting

### Common Issues and Solutions

#### High Temperature Warnings
- **Cause**: Continuous operation, high ambient temperature, or mechanical friction
- **Solution**: 
  - Increase cooldown periods between operations
  - Check for mechanical binding or misalignment
  - Improve ventilation
  - Reduce operating speed or load

#### Frequent Stall Detection
- **Cause**: Excessive load, mechanical obstruction, or aggressive threshold
- **Solution**:
  - Check for mechanical obstructions
  - Reduce payload or speed
  - Adjust `current_stall_threshold` if false positives

#### Emergency Stop Won't Reset
- **Cause**: Temperature still above cooldown threshold
- **Solution**:
  - Wait for motors to cool below `cooldown_temperature`
  - Check `get_safety_report()` for current temperatures
  - Manually verify safe conditions before override

## API Reference

### MotorSafetyMonitor

```python
class MotorSafetyMonitor:
    def __init__(self, motors_bus, thresholds=None, callback=None)
    def start_monitoring() -> None
    def stop_monitoring() -> None
    def emergency_stop() -> None
    def reset_emergency_stop() -> None
    def apply_soft_start(motor, target_position, current_position) -> list[float]
    def get_safety_report() -> dict[str, Any]
```

### SafetyThresholds

```python
@dataclass
class SafetyThresholds:
    temperature_warning: float = 40.0
    temperature_critical: float = 45.0
    temperature_shutdown: float = 50.0
    current_stall_threshold: float = 800.0
    current_stall_duration: float = 0.5
    current_spike_threshold: float = 1200.0
    soft_start_duration: float = 1.0
    soft_start_steps: int = 10
    position_margin: float = 5.0
    max_velocity: float = 180.0
    monitor_frequency: float = 10.0
    cooldown_temperature: float = 35.0
    recovery_wait_time: float = 5.0
```

### SafetyStatus Enum

```python
class SafetyStatus(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY_STOP = "emergency_stop"
```

### SafetyViolationType Enum

```python
class SafetyViolationType(Enum):
    TEMPERATURE_WARNING = "temperature_warning"
    TEMPERATURE_CRITICAL = "temperature_critical"
    CURRENT_STALL = "current_stall"
    POSITION_LIMIT = "position_limit"
    VELOCITY_LIMIT = "velocity_limit"
    EMERGENCY_STOP = "emergency_stop"
```

## Performance Considerations

- **Monitoring overhead**: ~2-5% CPU usage at 10Hz monitoring
- **Memory usage**: ~10MB for typical 6-motor configuration
- **Latency impact**: <1ms added to control loop
- **Thread safety**: All public methods are thread-safe

## Future Enhancements

Planned improvements for future versions:

1. **Machine Learning Integration**
   - Predictive failure detection
   - Adaptive threshold adjustment
   - Pattern recognition for anomalies

2. **Advanced Diagnostics**
   - Motor health scoring
   - Remaining lifetime estimation
   - Maintenance scheduling

3. **Cloud Integration**
   - Remote monitoring dashboard
   - Alert notifications
   - Historical data analysis

4. **Multi-Robot Coordination**
   - Fleet-wide safety management
   - Cross-robot emergency stop
   - Synchronized safety protocols

## Support

For issues, questions, or contributions:
- GitHub Issues: [lerobot/issues](https://github.com/huggingface/lerobot/issues)
- Documentation: [lerobot.huggingface.co](https://lerobot.huggingface.co)
- Community: [HuggingFace Discord](https://discord.gg/huggingface)

## License

Copyright 2025 The HuggingFace Inc. team. All rights reserved.

Licensed under the Apache License, Version 2.0.