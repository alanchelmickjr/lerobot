# LeKiwi Robot Calibration Issue Report

## Executive Summary

The LeKiwi robot system experiences unexpected calibration interruptions during host activation and after power resets. This report documents the technical investigation into the calibration system, identifies root causes of recalibration triggers, and provides recommendations for resolution.

---

## Problem Description

### Primary Issue
When the LeKiwi host is activated, the calibration process automatically initiates, causing:
- **Teleoperation cessation** due to blocking manual input requirements
- **Command processing interruption** preventing remote control
- **Unexpected recalibration** after power cycles or at seemingly random intervals

### Symptoms
1. Robot stops responding to teleoperation commands
2. System prompts for manual calibration input during operation
3. Previously calibrated robots require recalibration after power reset
4. Calibration state appears to be lost or corrupted intermittently

---

## Technical Analysis

### Calibration Trigger Mechanism

#### 1. Connection Flow
```
lekiwi_host.py:56 → robot.connect()
    ↓
lekiwi.py:116 → Checks: if not self.is_calibrated and calibrate
    ↓
lekiwi.py:129 → self.bus.is_calibrated
    ↓
feetech.py:232-250 → Compares stored vs actual motor values
    ↓
If mismatch → Triggers calibration
```

#### 2. Calibration Check Implementation

The [`FeetechMotorsBus.is_calibrated`](src/lerobot/motors/feetech/feetech.py:232-250) property performs the following validation:

```python
def is_calibrated(self) -> bool:
    motors_calibration = self.read_calibration()
    if set(motors_calibration) != set(self.calibration):
        return False

    same_ranges = all(
        self.calibration[motor].range_min == cal.range_min
        and self.calibration[motor].range_max == cal.range_max
        for motor, cal in motors_calibration.items()
    )
    if self.protocol_version == 1:
        return same_ranges

    same_offsets = all(
        self.calibration[motor].homing_offset == cal.homing_offset
        for motor, cal in motors_calibration.items()
    )
    return same_ranges and same_offsets
```

This checks:
- **Motor set match**: All expected motors are present
- **Range limits**: Min/max position limits match stored values
- **Homing offsets**: For protocol version 0, homing offsets must match

---

## Root Causes of Recalibration After Power Reset

### 1. **Motor State Volatility**
Feetech STS3215 motors may not retain certain configuration parameters after power loss:
- Homing offset values may reset to factory defaults (0)
- Position limits might revert to default values (0-4095)
- These values are stored in motor EEPROM but may not persist properly

### 2. **Calibration File Location**
Calibration files are stored at:
```
~/.cache/calibration/robots/lekiwi/{robot_id}.json
```

Issues that can occur:
- File permissions preventing read/write access
- File corruption during unexpected shutdown
- Multiple robot instances using conflicting IDs
- Network file systems causing sync issues

### 3. **Motor Communication Errors**
During startup, if motor communication fails:
- `read_calibration()` may return incomplete or incorrect values
- Transient communication errors trigger false calibration mismatches
- USB/serial connection instability after power cycle

### 4. **Protocol Version Confusion**
The code branches behavior based on `protocol_version`:
- Version 0: Checks homing offsets
- Version 1: Skips homing offset validation

If protocol version detection fails or changes, calibration validation behavior changes.

---

## Calibration Process Blocking Points

The [`LeKiwi.calibrate()`](src/lerobot/robots/lekiwi/lekiwi.py:132-181) method contains three blocking operations:

### 1. **User Choice Prompt** (Lines 135-141)
```python
user_input = input(
    f"Press ENTER to use provided calibration file associated with the id {self.id}, "
    "or type 'c' and press ENTER to run calibration: "
)
```
**Impact**: Blocks execution waiting for user input

### 2. **Manual Positioning** (Line 150)
```python
input("Move robot to the middle of its range of motion and press ENTER....")
```
**Impact**: Requires physical robot manipulation

### 3. **Range Recording** (Lines 161-164)
```python
print(
    f"Move all arm joints except '{full_turn_motor}' sequentially through their "
    "entire ranges of motion.\nRecording positions. Press ENTER to stop..."
)
range_mins, range_maxes = self.bus.record_ranges_of_motion(unknown_range_motors)
```
**Impact**: Requires continuous manual joint movement

---

## Why Power Reset Triggers Recalibration

### Scenario Analysis

#### Case 1: Clean Power Cycle
1. Robot powered off gracefully
2. Motor settings saved to EEPROM
3. Power restored
4. **Issue**: Motors may not load saved settings from EEPROM automatically
5. Default values don't match calibration file
6. Recalibration triggered

#### Case 2: Unexpected Power Loss
1. Robot loses power during operation
2. Motor settings not saved to EEPROM
3. Power restored with factory defaults
4. Calibration mismatch detected
5. Recalibration triggered

#### Case 3: USB/Serial Reset
1. Power cycle causes USB enumeration change
2. Serial port assignment changes (e.g., /dev/ttyACM0 → /dev/ttyACM1)
3. Connection fails or connects to wrong device
4. Calibration validation fails
5. Recalibration triggered

---

## Diagnostic Findings

### Critical Code Paths

1. **Host Initialization** [`lekiwi_host.py:56`]
   - Always calls `robot.connect()` with default `calibrate=True`
   - No configuration option to skip calibration

2. **Connection Logic** [`lekiwi.py:111-120`]
   - Automatically triggers calibration if `is_calibrated` returns `False`
   - No retry mechanism for transient failures

3. **Calibration Validation** [`feetech.py:232-250`]
   - Strict equality checks without tolerance
   - No handling of communication errors
   - No caching of successful validation

### Design Issues

1. **Synchronous Blocking Design**
   - Calibration uses blocking `input()` calls
   - Cannot be run in parallel with teleoperation
   - No timeout or skip mechanism

2. **No State Persistence**
   - Motors don't reliably persist calibration
   - No backup mechanism for calibration data
   - No validation of motor EEPROM state

3. **Error Handling**
   - No distinction between actual calibration need vs. communication error
   - No recovery mechanism for transient failures
   - No logging of calibration trigger reasons

---

## Recommendations

### Immediate Fix
Modify [`lekiwi_host.py:56`](src/lerobot/robots/lekiwi/lekiwi_host.py:56):
```python
# Change from:
robot.connect()
# To:
robot.connect(calibrate=False)
```

### Short-term Solutions

1. **Add Configuration Option**
```python
# In LeKiwiHostConfig
auto_calibrate: bool = False

# In main()
robot.connect(calibrate=host_config.auto_calibrate)
```

2. **Implement Calibration Check**
```python
# Before starting host
if not robot.is_calibrated:
    print("Warning: Robot not calibrated. Run calibration separately.")
    if not args.skip_calibration_check:
        sys.exit(1)
```

3. **Motor State Verification**
```python
# After power cycle, explicitly write calibration
robot.bus.write_calibration(robot.calibration)
```

### Long-term Solutions

1. **Persistent Motor Configuration**
   - Implement motor EEPROM write verification
   - Add calibration backup/restore mechanism
   - Create motor state validation on startup

2. **Non-blocking Calibration**
   - Separate calibration into standalone process
   - Implement web-based calibration interface
   - Add remote calibration capability

3. **Robust State Management**
   - Add calibration state caching with TTL
   - Implement calibration validation with tolerance
   - Add diagnostic logging for calibration triggers

4. **Error Recovery**
   - Retry logic for transient communication failures
   - Fallback to last known good calibration
   - Automatic calibration recovery mechanism

---

## Testing Recommendations

### Reproduce Issue
1. Calibrate robot successfully
2. Verify calibration file exists
3. Power cycle robot
4. Start host and observe calibration trigger

### Validation Tests
1. **Power Cycle Test**: Verify calibration persistence after power reset
2. **USB Disconnect Test**: Check behavior on USB reconnection
3. **Communication Error Test**: Simulate transient serial errors
4. **File Corruption Test**: Test with corrupted calibration file

### Monitoring
- Log all calibration trigger events with reasons
- Track motor state changes across power cycles
- Monitor serial communication stability

---

## Conclusion

The LeKiwi calibration interruption issue stems from:
1. Automatic calibration on host connection
2. Motor state volatility after power resets
3. Strict calibration validation without error tolerance
4. Blocking manual calibration process

The immediate fix is to disable automatic calibration in the host. Long-term solutions should focus on:
- Improving motor state persistence
- Implementing non-blocking calibration
- Adding robust error handling and recovery
- Providing configuration options for calibration behavior

This analysis provides the technical foundation for implementing both immediate fixes and long-term improvements to the LeKiwi calibration system.