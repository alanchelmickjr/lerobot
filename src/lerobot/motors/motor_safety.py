#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Motor Safety System for LeRobot

This module provides comprehensive safety monitoring and protection for robot motors,
including temperature monitoring, current-based stall detection, soft start functionality,
position limit enforcement, and emergency stop capabilities.
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

logger = logging.getLogger(__name__)


class SafetyStatus(Enum):
    """Safety system status states."""
    
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY_STOP = "emergency_stop"


class SafetyViolationType(Enum):
    """Types of safety violations that can occur."""
    
    TEMPERATURE_WARNING = "temperature_warning"
    TEMPERATURE_CRITICAL = "temperature_critical"
    CURRENT_STALL = "current_stall"
    POSITION_LIMIT = "position_limit"
    VELOCITY_LIMIT = "velocity_limit"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class SafetyThresholds:
    """Configuration for motor safety thresholds."""
    
    # Temperature thresholds (Celsius)
    temperature_warning: float = 40.0
    temperature_critical: float = 45.0
    temperature_shutdown: float = 50.0
    
    # Current thresholds (mA)
    current_stall_threshold: float = 800.0
    current_stall_duration: float = 0.5  # seconds
    current_spike_threshold: float = 1200.0
    
    # Soft start parameters
    soft_start_duration: float = 1.0  # seconds
    soft_start_steps: int = 10
    
    # Position safety
    position_margin: float = 5.0  # degrees from limits
    
    # Velocity limits (degrees/sec)
    max_velocity: float = 180.0
    
    # Monitoring rates
    monitor_frequency: float = 10.0  # Hz
    
    # Recovery parameters
    cooldown_temperature: float = 35.0
    recovery_wait_time: float = 5.0  # seconds


@dataclass
class MotorSafetyState:
    """State tracking for individual motor safety."""
    
    motor_name: str
    temperature: float = 0.0
    current: float = 0.0
    position: float = 0.0
    velocity: float = 0.0
    
    # Stall detection
    high_current_start_time: Optional[float] = None
    is_stalled: bool = False
    
    # Temperature tracking
    temperature_history: list = field(default_factory=list)
    max_temp_reached: float = 0.0
    
    # Violation tracking
    violations: list = field(default_factory=list)
    last_violation_time: Optional[float] = None
    
    # Soft start state
    soft_start_active: bool = False
    soft_start_progress: float = 0.0


class MotorSafetyMonitor:
    """
    Motor safety monitoring system.
    
    Provides real-time monitoring of motor health parameters and implements
    safety protocols to prevent damage.
    """
    
    def __init__(
        self,
        motors_bus,
        thresholds: Optional[SafetyThresholds] = None,
        callback: Optional[Callable] = None,
    ):
        """
        Initialize the motor safety monitor.
        
        Args:
            motors_bus: The motor bus instance to monitor
            thresholds: Safety threshold configuration
            callback: Optional callback for safety events
        """
        self.bus = motors_bus
        self.thresholds = thresholds or SafetyThresholds()
        self.callback = callback
        
        # Safety states for each motor
        self.motor_states = {
            motor: MotorSafetyState(motor_name=motor)
            for motor in self.bus.motors
        }
        
        # Global safety state
        self.status = SafetyStatus.NORMAL
        self.emergency_stop_active = False
        self.monitoring_active = False
        
        # Monitoring thread
        self._monitor_thread = None
        self._stop_event = threading.Event()
        
        # Safety statistics
        self.stats = {
            "total_violations": 0,
            "temperature_warnings": 0,
            "current_stalls": 0,
            "emergency_stops": 0,
            "uptime": 0.0,
        }
        
        self._start_time = time.time()
    
    def start_monitoring(self) -> None:
        """Start the safety monitoring thread."""
        if self.monitoring_active:
            logger.warning("Safety monitoring already active")
            return
        
        self.monitoring_active = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Motor safety monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop the safety monitoring thread."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        
        logger.info("Motor safety monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop running in separate thread."""
        monitor_period = 1.0 / self.thresholds.monitor_frequency
        
        while not self._stop_event.is_set():
            try:
                self._perform_safety_checks()
                time.sleep(monitor_period)
                self.stats["uptime"] = time.time() - self._start_time
            except Exception as e:
                logger.error(f"Error in safety monitor loop: {e}")
                time.sleep(monitor_period)
    
    def _perform_safety_checks(self) -> None:
        """Perform all safety checks on motors."""
        # Read current motor states
        temperatures = self.bus.sync_read("Present_Temperature")
        currents = self.bus.sync_read("Present_Current")
        positions = self.bus.sync_read("Present_Position")
        
        # Check each motor
        for motor in self.bus.motors:
            state = self.motor_states[motor]
            
            # Update state
            state.temperature = temperatures.get(motor, 0)
            state.current = abs(currents.get(motor, 0))
            state.position = positions.get(motor, 0)
            
            # Perform safety checks
            self._check_temperature(motor, state)
            self._check_current_stall(motor, state)
            self._check_position_limits(motor, state)
        
        # Update global safety status
        self._update_global_status()
    
    def _check_temperature(self, motor: str, state: MotorSafetyState) -> None:
        """Check temperature safety for a motor."""
        temp = state.temperature
        
        # Track temperature history
        state.temperature_history.append(temp)
        if len(state.temperature_history) > 100:
            state.temperature_history.pop(0)
        
        state.max_temp_reached = max(state.max_temp_reached, temp)
        
        # Check thresholds
        if temp >= self.thresholds.temperature_shutdown:
            self._handle_temperature_critical(motor, temp)
        elif temp >= self.thresholds.temperature_critical:
            self._handle_temperature_warning(motor, temp, is_critical=True)
        elif temp >= self.thresholds.temperature_warning:
            self._handle_temperature_warning(motor, temp, is_critical=False)
    
    def _check_current_stall(self, motor: str, state: MotorSafetyState) -> None:
        """Check for motor stall based on current draw."""
        current = state.current
        
        if current >= self.thresholds.current_spike_threshold:
            # Immediate response to current spike
            self._handle_current_spike(motor, current)
        elif current >= self.thresholds.current_stall_threshold:
            # Track duration of high current
            if state.high_current_start_time is None:
                state.high_current_start_time = time.time()
            else:
                duration = time.time() - state.high_current_start_time
                if duration >= self.thresholds.current_stall_duration:
                    state.is_stalled = True
                    self._handle_stall_detected(motor, current, duration)
        else:
            # Reset stall detection
            state.high_current_start_time = None
            state.is_stalled = False
    
    def _check_position_limits(self, motor: str, state: MotorSafetyState) -> None:
        """Check if motor is approaching position limits."""
        if motor not in self.bus.calibration:
            return
        
        cal = self.bus.calibration[motor]
        position = state.position
        
        # Check proximity to limits
        margin = self.thresholds.position_margin
        if position <= cal.range_min + margin or position >= cal.range_max - margin:
            self._handle_position_limit_warning(motor, position, cal.range_min, cal.range_max)
    
    def _handle_temperature_warning(self, motor: str, temp: float, is_critical: bool) -> None:
        """Handle temperature warning."""
        level = "CRITICAL" if is_critical else "WARNING"
        logger.warning(f"Temperature {level} for {motor}: {temp:.1f}°C")
        
        violation_type = (
            SafetyViolationType.TEMPERATURE_CRITICAL
            if is_critical
            else SafetyViolationType.TEMPERATURE_WARNING
        )
        
        self._record_violation(motor, violation_type, {"temperature": temp})
        
        if is_critical:
            # Reduce motor torque to prevent further heating
            self._reduce_motor_torque(motor, reduction=0.5)
    
    def _handle_temperature_critical(self, motor: str, temp: float) -> None:
        """Handle critical temperature - shut down motor."""
        logger.critical(f"Temperature SHUTDOWN for {motor}: {temp:.1f}°C")
        
        self._record_violation(motor, SafetyViolationType.TEMPERATURE_CRITICAL, {"temperature": temp})
        
        # Disable motor torque immediately
        self.bus.disable_torque(motor)
        
        # Trigger emergency stop if configured
        if self.callback:
            self.callback("temperature_shutdown", motor, temp)
    
    def _handle_current_spike(self, motor: str, current: float) -> None:
        """Handle current spike detection."""
        logger.warning(f"Current spike detected for {motor}: {current:.0f}mA")
        
        # Immediately reduce torque
        self._reduce_motor_torque(motor, reduction=0.3)
    
    def _handle_stall_detected(self, motor: str, current: float, duration: float) -> None:
        """Handle motor stall detection."""
        logger.error(f"Motor stall detected for {motor}: {current:.0f}mA for {duration:.1f}s")
        
        self._record_violation(motor, SafetyViolationType.CURRENT_STALL, {
            "current": current,
            "duration": duration
        })
        
        # Disable motor to prevent damage
        self.bus.disable_torque(motor)
        
        if self.callback:
            self.callback("stall_detected", motor, current)
    
    def _handle_position_limit_warning(
        self, motor: str, position: float, min_limit: float, max_limit: float
    ) -> None:
        """Handle position limit proximity warning."""
        logger.debug(f"Position limit warning for {motor}: {position:.1f} (limits: {min_limit:.1f}-{max_limit:.1f})")
        
        # Soft limit enforcement - reduce speed near limits
        if hasattr(self.bus, "write"):
            # Reduce velocity near limits
            self.bus.write("Goal_Velocity", motor, 50)
    
    def _reduce_motor_torque(self, motor: str, reduction: float = 0.5) -> None:
        """Reduce motor torque by specified factor."""
        try:
            if hasattr(self.bus, "read") and hasattr(self.bus, "write"):
                current_torque = self.bus.read("Torque_Limit", motor)
                reduced_torque = int(current_torque * reduction)
                self.bus.write("Torque_Limit", motor, reduced_torque)
                logger.info(f"Reduced torque for {motor} to {reduced_torque}")
        except Exception as e:
            logger.error(f"Failed to reduce torque for {motor}: {e}")
    
    def _record_violation(self, motor: str, violation_type: SafetyViolationType, data: dict) -> None:
        """Record a safety violation."""
        state = self.motor_states[motor]
        
        violation = {
            "time": time.time(),
            "type": violation_type,
            "data": data
        }
        
        state.violations.append(violation)
        state.last_violation_time = time.time()
        
        self.stats["total_violations"] += 1
        
        if violation_type in [SafetyViolationType.TEMPERATURE_WARNING, SafetyViolationType.TEMPERATURE_CRITICAL]:
            self.stats["temperature_warnings"] += 1
        elif violation_type == SafetyViolationType.CURRENT_STALL:
            self.stats["current_stalls"] += 1
    
    def _update_global_status(self) -> None:
        """Update global safety status based on individual motor states."""
        has_critical = False
        has_warning = False
        
        for state in self.motor_states.values():
            if state.is_stalled or state.temperature >= self.thresholds.temperature_critical:
                has_critical = True
            elif state.temperature >= self.thresholds.temperature_warning:
                has_warning = True
        
        if self.emergency_stop_active:
            self.status = SafetyStatus.EMERGENCY_STOP
        elif has_critical:
            self.status = SafetyStatus.CRITICAL
        elif has_warning:
            self.status = SafetyStatus.WARNING
        else:
            self.status = SafetyStatus.NORMAL
    
    def emergency_stop(self) -> None:
        """Trigger emergency stop - disable all motors immediately."""
        logger.critical("EMERGENCY STOP ACTIVATED")
        
        self.emergency_stop_active = True
        self.status = SafetyStatus.EMERGENCY_STOP
        
        # Disable all motors
        self.bus.disable_torque()
        
        self.stats["emergency_stops"] += 1
        
        if self.callback:
            self.callback("emergency_stop", None, None)
    
    def reset_emergency_stop(self) -> None:
        """Reset emergency stop after safety check."""
        if not self.emergency_stop_active:
            return
        
        # Check if it's safe to reset
        all_temps_safe = all(
            state.temperature < self.thresholds.cooldown_temperature
            for state in self.motor_states.values()
        )
        
        if not all_temps_safe:
            logger.warning("Cannot reset emergency stop - temperatures still too high")
            return
        
        self.emergency_stop_active = False
        logger.info("Emergency stop reset")
    
    def apply_soft_start(self, motor: str, target_position: float, current_position: float) -> list[float]:
        """
        Generate soft start trajectory for smooth motor startup.
        
        Args:
            motor: Motor name
            target_position: Target position
            current_position: Current position
            
        Returns:
            List of intermediate positions for soft start
        """
        state = self.motor_states[motor]
        state.soft_start_active = True
        
        # Generate smooth trajectory
        steps = self.thresholds.soft_start_steps
        positions = []
        
        for i in range(steps):
            progress = (i + 1) / steps
            # Use S-curve for smooth acceleration
            s_curve = 0.5 * (1 - np.cos(np.pi * progress))
            position = current_position + s_curve * (target_position - current_position)
            positions.append(position)
        
        state.soft_start_active = False
        return positions
    
    def get_safety_report(self) -> dict[str, Any]:
        """Get comprehensive safety status report."""
        return {
            "status": self.status.value,
            "emergency_stop": self.emergency_stop_active,
            "uptime": self.stats["uptime"],
            "statistics": self.stats,
            "motors": {
                motor: {
                    "temperature": state.temperature,
                    "max_temp": state.max_temp_reached,
                    "current": state.current,
                    "is_stalled": state.is_stalled,
                    "violations": len(state.violations),
                    "last_violation": state.last_violation_time
                }
                for motor, state in self.motor_states.items()
            }
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()