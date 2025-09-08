# SO101 Intelligent Auto-Calibration Implementation Plan

## Executive Summary

This document outlines the implementation of an intelligent auto-calibration system for the SO101 robot arm and teleoperator that integrates with LeRobot's calibration infrastructure. The system leverages servo telemetry to perform safe, automatic calibration without manual intervention, with built-in protection against overheating and overextension.

---

## Objectives

### Primary Goals
1. **Zero Manual Intervention**: Complete auto-calibration without user input
2. **Thermal Protection**: Automatic pause/stop on overheat conditions
3. **Overextension Prevention**: Detect and prevent mechanical damage
4. **Universal Application**: Work for both robot (follower) and teleoperator (leader)
5. **CLI Integration**: Seamless integration with `lerobot calibrate` command

### Safety Requirements
- Temperature threshold monitoring (stop at >45°C)
- Current-based stall detection (prevent motor damage)
- Gradual torque application (soft start)
- Position limit enforcement
- Emergency stop capability

---

## Architecture Overview

### Command Structure
```
lerobot calibrate --robot.type=so101 --mode=intelligent
lerobot calibrate --teleop.type=so101 --mode=intelligent
lerobot-calibrate-auto so101  # New dedicated command
```

### Core Components

```python
# File: src/lerobot/calibration/intelligent_calibrator.py

class IntelligentCalibrator:
    """Base class for intelligent auto-calibration."""
    
    def __init__(self, device, config):
        self.device = device
        self.config = config
        self.telemetry_monitor = TelemetryMonitor(device.bus)
        self.safety_system = SafetySystem(config.safety_thresholds)
        self.calibration_data = {}
    
    def calibrate(self) -> dict:
        """Main calibration entry point."""
        pass

class SO101Calibrator(IntelligentCalibrator):
    """SO101-specific intelligent calibration."""
    pass

class TelemetryMonitor:
    """Real-time servo telemetry monitoring."""
    pass

class SafetySystem:
    """Safety enforcement and emergency stop."""
    pass
```

---

## Implementation Details

### 1. Enhanced Calibration Command

#### Modified `src/lerobot/calibrate.py`
```python
import logging
from dataclasses import dataclass, field
from typing import Literal, Optional

from lerobot.calibration.intelligent_calibrator import get_intelligent_calibrator
from lerobot.robots.factory import make_robot_from_config
from lerobot.teleoperators.factory import make_teleoperator_from_config

@dataclass
class CalibrateConfig:
    teleop: TeleoperatorConfig | None = None
    robot: RobotConfig | None = None
    mode: Literal["manual", "intelligent", "auto"] = "manual"
    
    # Intelligent calibration options
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    
    def __post_init__(self):
        if bool(self.teleop) == bool(self.robot):
            raise ValueError("Choose either a teleop or a robot.")
        self.device = self.robot if self.robot else self.teleop

@dataclass 
class SafetyConfig:
    """Safety thresholds for intelligent calibration."""
    max_temperature_c: int = 45
    critical_temperature_c: int = 50
    max_current_ma: int = 1000
    stall_current_ma: int = 800
    torque_limit_calibration: int = 300  # 30% during calibration
    cooldown_wait_s: int = 30
    enable_emergency_stop: bool = True

@dataclass
class TelemetryConfig:
    """Telemetry monitoring configuration."""
    sample_rate_hz: float = 10.0
    history_size: int = 100
    log_telemetry: bool = True
    save_telemetry_file: Optional[str] = None

def calibrate(cfg: CalibrateConfig):
    """Enhanced calibration with intelligent mode support."""
    init_logging()
    logging.info(f"Calibration mode: {cfg.mode}")
    logging.info(pformat(asdict(cfg)))
    
    # Create device instance
    if isinstance(cfg.device, RobotConfig):
        device = make_robot_from_config(cfg.device)
        device_type = "robot"
    elif isinstance(cfg.device, TeleoperatorConfig):
        device = make_teleoperator_from_config(cfg.device)
        device_type = "teleoperator"
    
    # Connect without default calibration
    device.connect(calibrate=False)
    
    try:
        if cfg.mode == "intelligent" or cfg.mode == "auto":
            # Use intelligent calibration
            calibrator = get_intelligent_calibrator(
                device=device,
                device_type=device_type,
                safety_config=cfg.safety,
                telemetry_config=cfg.telemetry
            )
            
            logging.info("Starting intelligent auto-calibration...")
            success = calibrator.calibrate()
            
            if not success:
                logging.warning("Intelligent calibration failed, falling back to manual")
                device.calibrate()  # Fall back to manual
        else:
            # Traditional manual calibration
            device.calibrate()
    
    finally:
        device.disconnect()
```

### 2. Intelligent Calibrator Implementation

#### File: `src/lerobot/calibration/intelligent_calibrator.py`
```python
import time
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np

from lerobot.motors import MotorCalibration

logger = logging.getLogger(__name__)

class IntelligentCalibrator(ABC):
    """Base class for intelligent auto-calibration with safety features."""
    
    def __init__(self, device, safety_config, telemetry_config):
        self.device = device
        self.bus = device.bus
        self.safety_config = safety_config
        self.telemetry_config = telemetry_config
        
        # Initialize monitoring systems
        self.telemetry_monitor = TelemetryMonitor(self.bus, telemetry_config)
        self.safety_system = SafetySystem(self.bus, safety_config)
        self.stall_detector = StallDetector(self.bus)
        
        # Calibration state
        self.calibration = {}
        self.calibration_success = False
        
    def calibrate(self) -> bool:
        """
        Main calibration routine with safety checks.
        
        Returns:
            bool: True if calibration successful, False otherwise
        """
        try:
            # Pre-calibration checks
            if not self._pre_calibration_checks():
                return False
            
            # Initialize safety systems
            self.safety_system.enable()
            self.telemetry_monitor.start()
            
            # Disable torque for initial assessment
            self.bus.disable_torque()
            time.sleep(0.5)
            
            # Calibrate baseline current
            logger.info("Calibrating baseline current...")
            self.stall_detector.calibrate_baseline(list(self.bus.motors.keys()))
            
            # Perform calibration for each motor
            for motor_name in self._get_calibration_order():
                logger.info(f"Calibrating {motor_name}...")
                
                # Check temperature before calibrating
                if not self.safety_system.check_temperature(motor_name):
                    logger.warning(f"Skipping {motor_name} - temperature too high")
                    continue
                
                # Calibrate motor
                motor_cal = self._calibrate_motor(motor_name)
                if motor_cal:
                    self.calibration[motor_name] = motor_cal
                else:
                    logger.error(f"Failed to calibrate {motor_name}")
                    return False
                
                # Cool down period between motors
                time.sleep(1)
            
            # Apply safety margins
            self._apply_safety_margins()
            
            # Write calibration to device
            self.bus.write_calibration(self.calibration)
            self.device._save_calibration()
            
            logger.info("Intelligent calibration completed successfully!")
            self.calibration_success = True
            return True
            
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False
            
        finally:
            # Cleanup
            self.safety_system.disable()
            self.telemetry_monitor.stop()
            self.bus.disable_torque()
    
    @abstractmethod
    def _calibrate_motor(self, motor_name: str) -> Optional[MotorCalibration]:
        """Calibrate a single motor - implement in subclass."""
        pass
    
    @abstractmethod
    def _get_calibration_order(self) -> List[str]:
        """Return motor calibration order - implement in subclass."""
        pass
    
    def _pre_calibration_checks(self) -> bool:
        """Perform pre-calibration safety checks."""
        logger.info("Performing pre-calibration checks...")
        
        # Check all motors are responding
        for motor in self.bus.motors:
            try:
                temp = self.bus.read("Present_Temperature", motor)
                if temp > self.safety_config.critical_temperature_c:
                    logger.error(f"{motor} is too hot: {temp}°C")
                    return False
            except Exception as e:
                logger.error(f"Cannot communicate with {motor}: {e}")
                return False
        
        return True
    
    def _apply_safety_margins(self):
        """Apply safety margins to calibration limits."""
        margin = 100  # Raw units
        for motor, cal in self.calibration.items():
            cal.range_min += margin
            cal.range_max -= margin


class SO101Calibrator(IntelligentCalibrator):
    """SO101-specific intelligent calibration implementation."""
    
    def _get_calibration_order(self) -> List[str]:
        """SO101 calibration order - start with base, end with gripper."""
        # Customize order based on SO101 structure
        order = []
        
        # Base first (if applicable)
        for motor in self.bus.motors:
            if "waist" in motor or "base" in motor:
                order.append(motor)
        
        # Then shoulder to wrist
        for motor in self.bus.motors:
            if "shoulder" in motor:
                order.append(motor)
        for motor in self.bus.motors:
            if "elbow" in motor:
                order.append(motor)
        for motor in self.bus.motors:
            if "wrist" in motor and "roll" not in motor:
                order.append(motor)
        
        # Continuous rotation joints
        for motor in self.bus.motors:
            if "roll" in motor or "rotate" in motor:
                order.append(motor)
        
        # Gripper last
        for motor in self.bus.motors:
            if "gripper" in motor or "hand" in motor:
                order.append(motor)
        
        # Add any remaining motors
        for motor in self.bus.motors:
            if motor not in order:
                order.append(motor)
        
        return order
    
    def _calibrate_motor(self, motor_name: str) -> Optional[MotorCalibration]:
        """Calibrate a single SO101 motor with intelligent limit finding."""
        
        # Enable torque with low limit for safety
        self.bus.write("Torque_Limit", motor_name, self.safety_config.torque_limit_calibration)
        self.bus.write("Torque_Enable", motor_name, 1)
        
        # Get current position
        start_pos = self.bus.read("Present_Position", motor_name)
        
        # Special handling for different joint types
        if "roll" in motor_name or "rotate" in motor_name:
            # Continuous rotation joint
            return self._calibrate_continuous(motor_name, start_pos)
        elif "gripper" in motor_name:
            # Gripper has limited range
            return self._calibrate_gripper(motor_name, start_pos)
        else:
            # Standard limited joint
            return self._calibrate_limited(motor_name, start_pos)
    
    def _calibrate_limited(self, motor_name: str, start_pos: int) -> Optional[MotorCalibration]:
        """Calibrate a joint with physical limits."""
        
        # Find lower limit
        logger.info(f"  Finding lower limit for {motor_name}...")
        lower_limit = self._find_limit(motor_name, direction=-1, start_pos=start_pos)
        
        if lower_limit is None:
            logger.error(f"  Failed to find lower limit for {motor_name}")
            return None
        
        # Return to safe position
        mid_pos = start_pos
        self._safe_move_to(motor_name, mid_pos)
        time.sleep(0.5)
        
        # Find upper limit
        logger.info(f"  Finding upper limit for {motor_name}...")
        upper_limit = self._find_limit(motor_name, direction=1, start_pos=start_pos)
        
        if upper_limit is None:
            logger.error(f"  Failed to find upper limit for {motor_name}")
            return None
        
        # Calculate calibration
        center = (lower_limit + upper_limit) // 2
        homing_offset = center - 2048
        
        logger.info(f"  {motor_name}: limits [{lower_limit}, {upper_limit}], center {center}")
        
        return MotorCalibration(
            id=self.bus.motors[motor_name].id,
            drive_mode=0,
            homing_offset=homing_offset,
            range_min=lower_limit,
            range_max=upper_limit
        )
    
    def _calibrate_continuous(self, motor_name: str, start_pos: int) -> MotorCalibration:
        """Calibrate continuous rotation joint (full 360°)."""
        logger.info(f"  {motor_name} is continuous rotation")
        
        return MotorCalibration(
            id=self.bus.motors[motor_name].id,
            drive_mode=0,
            homing_offset=start_pos - 2048,
            range_min=0,
            range_max=4095
        )
    
    def _calibrate_gripper(self, motor_name: str, start_pos: int) -> Optional[MotorCalibration]:
        """Calibrate gripper with gentle limits."""
        logger.info(f"  Calibrating gripper {motor_name}...")
        
        # Use even lower torque for gripper
        self.bus.write("Torque_Limit", motor_name, 200)
        
        # Find closed position (lower limit)
        closed_pos = self._find_limit(motor_name, direction=-1, start_pos=start_pos, 
                                     max_travel=1500)
        
        # Find open position (upper limit)
        self._safe_move_to(motor_name, start_pos)
        open_pos = self._find_limit(motor_name, direction=1, start_pos=start_pos,
                                   max_travel=1500)
        
        if closed_pos is None or open_pos is None:
            return None
        
        return MotorCalibration(
            id=self.bus.motors[motor_name].id,
            drive_mode=0,
            homing_offset=0,
            range_min=closed_pos,
            range_max=open_pos
        )
    
    def _find_limit(self, motor_name: str, direction: int, start_pos: int,
                    max_travel: int = 3000) -> Optional[int]:
        """Find physical limit using stall detection with safety checks."""
        
        current_pos = start_pos
        step_size = 50
        consecutive_stalls = 0
        
        while abs(current_pos - start_pos) < max_travel:
            # Safety checks
            if not self.safety_system.check_all(motor_name):
                logger.warning(f"  Safety stop triggered for {motor_name}")
                return current_pos
            
            # Move one step
            target_pos = current_pos + (step_size * direction)
            self.bus.write("Goal_Position", motor_name, target_pos)
            time.sleep(0.2)
            
            # Check for stall
            is_stalled, diagnostics = self.stall_detector.detect_stall(motor_name)
            
            if is_stalled:
                consecutive_stalls += 1
                logger.debug(f"  Stall detected ({consecutive_stalls}): {diagnostics}")
                
                if consecutive_stalls >= 2:
                    # Confirmed limit reached
                    limit_pos = self.bus.read("Present_Position", motor_name)
                    
                    # Back off from limit
                    safe_pos = limit_pos - (step_size * direction * 3)
                    self._safe_move_to(motor_name, safe_pos)
                    
                    logger.info(f"  Found limit at position {limit_pos}")
                    return limit_pos
            else:
                consecutive_stalls = 0
                current_pos = self.bus.read("Present_Position", motor_name)
        
        # Reached max travel
        logger.warning(f"  No limit found within {max_travel} units")
        return current_pos
    
    def _safe_move_to(self, motor_name: str, position: int):
        """Safely move motor to position with monitoring."""
        # Set safe speed
        self.bus.write("Moving_Speed", motor_name, 200)
        self.bus.write("Goal_Position", motor_name, position)
        
        # Wait for movement with timeout
        timeout = 3.0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.bus.read("Moving", motor_name):
                break
            
            # Check safety during movement
            if not self.safety_system.check_all(motor_name):
                self.bus.write("Torque_Enable", motor_name, 0)
                raise RuntimeError(f"Safety stop during movement of {motor_name}")
            
            time.sleep(0.05)


class TelemetryMonitor:
    """Real-time telemetry monitoring and logging."""
    
    def __init__(self, bus, config):
        self.bus = bus
        self.config = config
        self.telemetry_history = defaultdict(list)
        self.is_running = False
        self._thread = None
    
    def start(self):
        """Start telemetry monitoring in background."""
        self.is_running = True
        if self.config.log_telemetry:
            import threading
            self._thread = threading.Thread(target=self._monitor_loop)
            self._thread.start()
    
    def stop(self):
        """Stop telemetry monitoring."""
        self.is_running = False
        if self._thread:
            self._thread.join()
        
        if self.config.save_telemetry_file:
            self._save_telemetry()
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.is_running:
            for motor in self.bus.motors:
                try:
                    telemetry = {
                        "timestamp": time.time(),
                        "position": self.bus.read("Present_Position", motor),
                        "temperature": self.bus.read("Present_Temperature", motor),
                        "current": self.bus.read("Present_Current", motor),
                        "load": self.bus.read("Present_Load", motor),
                    }
                    
                    self.telemetry_history[motor].append(telemetry)
                    
                    # Limit history size
                    if len(self.telemetry_history[motor]) > self.config.history_size:
                        self.telemetry_history[motor].pop(0)
                        
                except Exception as e:
                    logger.debug(f"Telemetry read error for {motor}: {e}")
            
            time.sleep(1.0 / self.config.sample_rate_hz)
    
    def get_latest(self, motor: str) -> dict:
        """Get latest telemetry for a motor."""
        if motor in self.telemetry_history and self.telemetry_history[motor]:
            return self.telemetry_history[motor][-1]
        return {}
    
    def _save_telemetry(self):
        """Save telemetry data to file."""
        if not self.telemetry_history:
            return
        
        import json
        with open(self.config.save_telemetry_file, 'w') as f:
            json.dump(dict(self.telemetry_history), f, indent=2, default=str)
        
        logger.info(f"Telemetry saved to {self.config.save_telemetry_file}")


class SafetySystem:
    """Safety monitoring and enforcement."""
    
    def __init__(self, bus, config):
        self.bus = bus
        self.config = config
        self.enabled = False
        self.emergency_stopped = False
    
    def enable(self):
        """Enable safety monitoring."""
        self.enabled = True
        self.emergency_stopped = False
        logger.info("Safety system enabled")
    
    def disable(self):
        """Disable safety monitoring."""
        self.enabled = False
    
    def check_all(self, motor: str) -> bool:
        """Check all safety conditions for a motor."""
        if not self.enabled:
            return True
        
        if self.emergency_stopped:
            return False
        
        return (self.check_temperature(motor) and 
                self.check_current(motor))
    
    def check_temperature(self, motor: str) -> bool:
        """Check if motor temperature is safe."""
        try:
            temp = self.bus.read("Present_Temperature", motor)
            
            if temp > self.config.critical_temperature_c:
                logger.error(f"CRITICAL: {motor} temperature {temp}°C exceeds critical threshold!")
                if self.config.enable_emergency_stop:
                    self.emergency_stop()
                return False
            
            if temp > self.config.max_temperature_c:
                logger.warning(f"{motor} temperature {temp}°C exceeds safe threshold")
                # Wait for cooldown
                return self._wait_for_cooldown(motor)
            
            return True
            
        except Exception as e:
            logger.error(f"Temperature check failed for {motor}: {e}")
            return False
    
    def check_current(self, motor: str) -> bool:
        """Check if motor current is safe."""
        try:
            current = self.bus.read("Present_Current", motor)
            
            if current > self.config.max_current_ma:
                logger.warning(f"{motor} current {current}mA exceeds maximum")
                return False
            
            return True
            
        except Exception:
            return True  # Don't fail on current read errors
    
    def _wait_for_cooldown(self, motor: str) -> bool:
        """Wait for motor to cool down."""
        logger.info(f"Waiting for {motor} to cool down...")
        
        start_time = time.time()
        max_wait = self.config.cooldown_wait_s
        
        while time.time() - start_time < max_wait:
            temp = self.bus.read("Present_Temperature", motor)
            
            if temp <= self.config.max_temperature_c - 5:  # 5°C buffer
                logger.info(f"{motor} cooled to {temp}°C")
                return True
            
            time.sleep(2)
        
        logger.error(f"{motor} failed to cool down in {max_wait}s")
        return False
    
    def emergency_stop(self):
        """Execute emergency stop."""
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.emergency_stopped = True
        
        # Disable all motor torques immediately
        try:
            for motor in self.bus.motors:
                self.bus.write("Torque_Enable", motor, 0)
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")


class StallDetector:
    """Motor stall detection based on current and movement."""
    
    def __init__(self, bus):
        self.bus = bus
        self.baseline_current = {}
        self.position_history = defaultdict(list)
    
    def calibrate_baseline(self, motors: List[str]):
        """Calibrate baseline current for motors."""
        for motor in motors:
            # Enable torque briefly to get baseline
            self.bus.write("Torque_Enable", motor, 1)
            time.sleep(0.1)
            
            # Read baseline current
            baseline = self.bus.read("Present_Current", motor)
            self.baseline_current[motor] = max(baseline, 100)  # Minimum baseline
            
            # Disable torque
            self.bus.write("Torque_Enable", motor, 0)
            
            logger.debug(f"Baseline current for {motor}: {baseline}mA")
    
    def detect_stall(self, motor: str) -> Tuple[bool, dict]:
        """
        Detect if motor is stalled.
        
        Returns:
            (is_stalled, diagnostics_dict)
        """
        try:
            # Read current state
            current = self.bus.read("Present_Current", motor)
            position = self.bus.read("Present_Position", motor)
            load = self.bus.read("Present_Load", motor)
            moving = self.bus.read("Moving", motor)
            goal = self.bus.read("Goal_Position", motor)
            
            # Track position history
            self.position_history[motor].append(position)
            if len(self.position_history[motor]) > 5:
                self.position_history[motor].pop(0)
            
            # Determine if stalled
            baseline = self.baseline_current.get(motor, 200)
            high_current = current > baseline * 2.5
            high_load = load > 800
            
            # Check if motor is stuck (not reaching goal)
            position_stuck = False
            if len(self.position_history[motor]) >= 3:
                positions = self.position_history[motor][-3:]
                position_variance = max(positions) - min(positions)
                position_stuck = position_variance < 10 and abs(position - goal) > 50
            
            is_stalled = (high_current and high_load) or (high_current and position_stuck)
            
            diagnostics = {
                "current": current,
                "baseline": baseline,
                "load": load,
                "position": position,
                "goal": goal,
                "moving": moving,
                "high_current": high_current,
                "high_load": high_load,
                "position_stuck": position_stuck
            }
            
            return is_stalled, diagnostics
            
        except Exception as e:
            logger.debug(f"Stall detection error for {motor}: {e}")
            return False, {"error": str(e)}


def get_intelligent_calibrator(device, device_type: str, 
                              safety_config, telemetry_config) -> IntelligentCalibrator:
    """Factory function to get appropriate calibrator for device."""
    
    device_name = device.name if hasattr(device, 'name') else device.__class__.__name__
    
    if "so101" in device_name.lower():
        return SO101Calibrator(device, safety_config, telemetry_config)
    elif "so100" in device_name.lower():
        # Could create SO100Calibrator
        return SO101Calibrator(device, safety_config, telemetry_config)  # Use same for now
    elif "koch" in device_name.lower():
        # Could create KochCalibrator
        return SO101Calibrator(device, safety_config, telemetry_config)
    else:
        # Default to SO101 calibrator as it's fairly generic
        logger.warning(f"No specific calibrator for {device_name}, using SO101Calibrator")
        return SO101Calibrator(device, safety_config, telemetry_config)
```

### 3. New CLI Command

#### File: `src/lerobot/scripts/auto_calibrate.py`
```python
#!/usr/bin/env python
"""
Standalone intelligent auto-calibration command.

Usage:
    lerobot-auto-calibrate so101 --device robot
    lerobot-auto-calibrate so101 --device teleop
    lerobot-auto-calibrate --list-devices
"""

import argparse
import sys
import logging
from pathlib import Path

from lerobot.calibrate import CalibrateConfig, SafetyConfig, TelemetryConfig, calibrate
from lerobot.robots.config import RobotConfig
from lerobot.teleoperators.config import TeleoperatorConfig

logger = logging.getLogger(__name__)

SUPPORTED_DEVICES = {
    "robots": ["so101", "so100", "koch", "lekiwi", "viperx"],
    "teleops": ["so101", "so100", "koch", "widowx"]
}

def main():
    parser = argparse.ArgumentParser(
        description="Intelligent auto-calibration for LeRobot devices"
    )
    
    parser.add_argument(
        "device_type",
        nargs="?",
        help="Device type (e.g., so101, koch)"
    )
    
    parser.add_argument(
        "--device",
        choices=["robot", "teleop"],
        default="robot",
        help="Device category"
    )
    
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List supported devices"
    )
    
    # Safety options
    parser.add_argument(
        "--max-temp",
        type=int,
        default=45,
        help="Maximum safe temperature (°C)"
    )
    
    parser.add_argument(
        "--max-current",
        type=int,
        default=1000,
        help="Maximum current (mA)"
    )
    
    parser.add_argument(
        "--torque-limit",
        type=int,
        default=300,
        help="Torque limit during calibration (0-1000)"
    )
    
    # Telemetry options
    parser.add_argument(
        "--save-telemetry",
        type=str,
        help="Save telemetry data to file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handle list devices
    if args.list_devices:
        print("\nSupported devices for intelligent auto-calibration:")
        print("\nRobots:")
        for robot in SUPPORTED_DEVICES["robots"]:
            print(f"  - {robot}")
        print("\nTeleoperators:")
        for teleop in SUPPORTED_DEVICES["teleops"]:
            print(f"  - {teleop}")
        return 0
    
    # Check device type
    if not args.device_type:
        parser.error("Device type required (or use --list-devices)")
    
    device_type = args.device_type.lower()
    
    # Validate device support
    if args.device == "robot" and device_type not in SUPPORTED_DEVICES["robots"]:
        logger.error(f"Robot '{device_type}' not supported for auto-calibration")
        logger.info(f"Supported robots: {', '.join(SUPPORTED_DEVICES['robots'])}")
        return 1
    
    if args.device == "teleop" and device_type not in SUPPORTED_DEVICES["teleops"]:
        logger.error(f"Teleoperator '{device_type}' not supported for auto-calibration")
        logger.info(f"Supported teleops: {', '.join(SUPPORTED_DEVICES['teleops'])}")
        return 1
    
    # Create configuration
    safety_config = SafetyConfig(
        max_temperature_c=args.max_temp,
        max_current_ma=args.max_current,
        torque_limit_calibration=args.torque_limit
    )
    
    telemetry_config = TelemetryConfig(
        save_telemetry_file=args.save_telemetry,
        log_telemetry=args.verbose
    )
    
    # Create device config
    if args.device == "robot":
        # Import specific robot config
        if device_type == "so101":
            from lerobot.robots.so101_follower import SO101FollowerConfig
            device_config = SO101FollowerConfig()
        elif device_type == "so100":
            from lerobot.robots.so100_follower import SO100FollowerConfig
            device_config = SO100FollowerConfig()
        else:
            logger.error(f"Config not found for robot {device_type}")
            return 1
            
        config = CalibrateConfig(
            robot=device_config,
            mode="intelligent",
            safety=safety_config,
            telemetry=telemetry_config
        )
    else:  # teleop
        # Import specific teleop config
        if device_type == "so101":
            from lerobot.teleoperators.so101_leader import SO101LeaderConfig
            device_config = SO101LeaderConfig()
        elif device_type == "so100":
            from lerobot.teleoperators.so100_leader import SO100LeaderConfig
            device_config = SO100LeaderConfig()
        else:
            logger.error(f"Config not found for teleop {device_type}")
            return 1
            
        config = CalibrateConfig(
            teleop=device_config,
            mode="intelligent",
            safety=safety_config,
            telemetry=telemetry_config
        )
    
    # Run calibration
    logger.info(f"Starting intelligent auto-calibration for {device_type} {args.device}")
    logger.info(f"Safety: max_temp={args.max_temp}°C, max_current={args.max_current}mA")
    
    try:
        calibrate(config)
        logger.info("Auto-calibration completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Auto-calibration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## Usage Examples

### Basic Usage
```bash
# Auto-calibrate SO101 robot
lerobot calibrate --robot.type=so101 --mode=intelligent

# Auto-calibrate SO101 teleoperator
lerobot calibrate --teleop.type=so101 --mode=intelligent

# Using new dedicated command
lerobot-auto-calibrate so101 --device robot
lerobot-auto-calibrate so101 --device teleop --save-telemetry calibration_data.json
```

### Advanced Usage
```bash
# Custom safety thresholds
lerobot-auto-calibrate so101 \
    --max-temp 40 \
    --max-current 800 \
    --torque-limit 250 \
    --save-telemetry telemetry.json \
    --verbose

# Skip calibration in existing commands
lerobot record --robot.type=so101 --skip-calibration
lerobot teleoperate --robot.type=so101 --calibration-mode=skip
```

---

## Integration Points

### 1. Existing Commands Enhancement
```python
# In lerobot/record.py
@dataclass
class RecordConfig:
    # ... existing fields ...
    calibration_mode: Literal["manual", "intelligent", "skip"] = "manual"

# In lerobot/teleoperate.py  
@dataclass
class TeleoperateConfig:
    # ... existing fields ...
    calibration_mode: Literal["manual", "intelligent", "skip"] = "manual"
```

### 2. Robot/Teleop Connection
```python
# Modified robot.connect() method
def connect(self, calibrate: bool = True, calibration_mode: str = "manual"):
    # ... connection logic ...
    
    if calibrate and not self.is_calibrated:
        if calibration_mode == "intelligent":
            from lerobot.calibration.intelligent_calibrator import get_intelligent_calibrator
            calibrator = get_intelligent_calibrator(self, "robot", 
                                                   SafetyConfig(), TelemetryConfig())
            if not calibrator.calibrate():
                # Fall back to manual
                self.calibrate()
        else:
            self.calibrate()
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_intelligent_calibration.py

def test_stall_detection():
    """Test stall detection algorithm."""
    pass

def test_temperature_safety():
    """Test temperature monitoring and safety stop."""
    pass

def test_calibration_limits():
    """Test limit finding algorithm."""
    pass

def test_emergency_stop():
    """Test emergency stop functionality."""
    pass
```

### Integration Tests
```python
def test_so101_auto_calibration():
    """Test full SO101 auto-calibration."""
    pass

def test_calibration_fallback():
    """Test fallback to manual calibration on failure."""
    pass

def test_telemetry_recording():
    """Test telemetry data recording during calibration."""
    pass
```

### Hardware Tests
1. **Thermal Test**: Run calibration on pre-heated motors
2. **Obstruction Test**: Place obstacles to test stall detection
3. **Power Cycle Test**: Verify calibration persistence
4. **Stress Test**: Multiple consecutive calibrations

---

## Safety Validation

### Critical Safety Features
1. **Temperature Protection**
   - Warning at 40°C
   - Pause at 45°C
   - Emergency stop at 50°C

2. **Current Limiting**
   - 30% torque during calibration
   - Stall detection at 2.5x baseline
   - Emergency stop at 1200mA

3. **Position Safety**
   - 100 unit margin from detected limits
   - Gradual torque application
   - Back-off on stall detection

4. **Emergency Stop**
   - Immediate torque disable
   - Non-recoverable state
   - Logged with full diagnostics

---

## Performance Metrics

### Target Specifications
- **Calibration Time**: <60 seconds for SO101 (6 motors)
- **Success Rate**: >99% without manual intervention
- **Temperature Rise**: <10°C during calibration
- **Safety Events**: 0 motor damage incidents
- **Accuracy**: ±50 raw units from optimal limits

### Monitoring Dashboard
```python
# Real-time monitoring during calibration
{
    "status": "calibrating",
    "current_motor": "shoulder_lift",
    "progress": "3/6 motors",
    "temperatures": {
        "waist": 32,
        "shoulder_pan": 34,
        "shoulder_lift": 38
    },
    "time_elapsed": 23.5,
    "estimated_remaining": 35.2
}
```

---

## Rollout Plan

### Phase 1: Development (Week 1-2)
- Implement core intelligent calibrator
- Add safety systems
- Create CLI command

### Phase 2: Testing (Week 3)
- Unit and integration tests
- Hardware validation
- Safety verification

### Phase 3: Beta Release (Week 4)
- Limited deployment
- Collect telemetry data
- Refine thresholds

### Phase 4: Production (Week 5)
- Full release
- Documentation
- Training materials

---

## Conclusion

This intelligent auto-calibration system for SO101 (and other LeRobot devices) provides:

1. **Complete Automation**: Zero manual intervention required
2. **Comprehensive Safety**: Multi-layered protection against damage
3. **Universal Application**: Works for both robots and teleoperators
4. **Seamless Integration**: Compatible with existing LeRobot commands
5. **Robust Operation**: Handles edge cases and failures gracefully

The system leverages servo telemetry to perform safe, automatic calibration while protecting against overheating and overextension, making robot setup accessible to users of all skill levels.