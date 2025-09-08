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

"""Tests for motor safety monitoring system."""

import time
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from lerobot.motors.motor_safety import (
    MotorSafetyMonitor,
    MotorSafetyState,
    SafetyStatus,
    SafetyThresholds,
    SafetyViolationType,
)


class TestSafetyThresholds(unittest.TestCase):
    """Test SafetyThresholds dataclass."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        thresholds = SafetyThresholds()
        
        # Temperature thresholds
        self.assertEqual(thresholds.temperature_warning, 40.0)
        self.assertEqual(thresholds.temperature_critical, 45.0)
        self.assertEqual(thresholds.temperature_shutdown, 50.0)
        
        # Current thresholds
        self.assertEqual(thresholds.current_stall_threshold, 800.0)
        self.assertEqual(thresholds.current_stall_duration, 0.5)
        
        # Soft start parameters
        self.assertEqual(thresholds.soft_start_duration, 1.0)
        self.assertEqual(thresholds.soft_start_steps, 10)

    def test_custom_thresholds(self):
        """Test custom threshold values."""
        thresholds = SafetyThresholds(
            temperature_warning=35.0,
            temperature_critical=42.0,
            current_stall_threshold=600.0,
        )
        
        self.assertEqual(thresholds.temperature_warning, 35.0)
        self.assertEqual(thresholds.temperature_critical, 42.0)
        self.assertEqual(thresholds.current_stall_threshold, 600.0)


class TestMotorSafetyState(unittest.TestCase):
    """Test MotorSafetyState dataclass."""

    def test_initial_state(self):
        """Test initial state values."""
        state = MotorSafetyState(motor_name="test_motor")
        
        self.assertEqual(state.motor_name, "test_motor")
        self.assertEqual(state.temperature, 0.0)
        self.assertEqual(state.current, 0.0)
        self.assertFalse(state.is_stalled)
        self.assertIsNone(state.high_current_start_time)
        self.assertEqual(len(state.violations), 0)


class TestMotorSafetyMonitor(unittest.TestCase):
    """Test MotorSafetyMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock motor bus
        self.mock_bus = MagicMock()
        self.mock_bus.motors = {"motor1": MagicMock(), "motor2": MagicMock()}
        self.mock_bus.calibration = {
            "motor1": MagicMock(range_min=0, range_max=100),
            "motor2": MagicMock(range_min=-50, range_max=50),
        }
        
        # Create safety monitor
        self.monitor = MotorSafetyMonitor(
            self.mock_bus,
            thresholds=SafetyThresholds(monitor_frequency=100),  # High frequency for testing
        )

    def tearDown(self):
        """Clean up after tests."""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()

    def test_initialization(self):
        """Test monitor initialization."""
        self.assertEqual(len(self.monitor.motor_states), 2)
        self.assertIn("motor1", self.monitor.motor_states)
        self.assertIn("motor2", self.monitor.motor_states)
        self.assertEqual(self.monitor.status, SafetyStatus.NORMAL)
        self.assertFalse(self.monitor.emergency_stop_active)

    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        # Start monitoring
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)

    def test_temperature_warning(self):
        """Test temperature warning detection."""
        # Mock temperature readings
        self.mock_bus.sync_read.return_value = {
            "motor1": 42.0,  # Above warning threshold
            "motor2": 30.0,  # Normal
        }
        
        # Perform safety check
        self.monitor._perform_safety_checks()
        
        # Check motor1 state
        state1 = self.monitor.motor_states["motor1"]
        self.assertEqual(state1.temperature, 42.0)
        self.assertTrue(len(state1.violations) > 0)
        
        # Check motor2 state
        state2 = self.monitor.motor_states["motor2"]
        self.assertEqual(state2.temperature, 30.0)

    def test_temperature_critical(self):
        """Test critical temperature detection."""
        # Mock temperature readings
        self.mock_bus.sync_read.side_effect = [
            {"motor1": 46.0, "motor2": 30.0},  # Temperature
            {"motor1": 500, "motor2": 200},    # Current
            {"motor1": 50, "motor2": 0},       # Position
        ]
        
        # Perform safety check
        self.monitor._perform_safety_checks()
        
        # Check motor1 received torque reduction
        self.mock_bus.read.assert_called()
        
        # Check status
        self.monitor._update_global_status()
        self.assertEqual(self.monitor.status, SafetyStatus.CRITICAL)

    def test_temperature_shutdown(self):
        """Test temperature shutdown."""
        # Mock temperature readings
        self.mock_bus.sync_read.side_effect = [
            {"motor1": 51.0, "motor2": 30.0},  # Above shutdown threshold
            {"motor1": 500, "motor2": 200},    # Current
            {"motor1": 50, "motor2": 0},       # Position
        ]
        
        # Perform safety check
        self.monitor._perform_safety_checks()
        
        # Check motor1 was disabled
        self.mock_bus.disable_torque.assert_called_with("motor1")

    def test_current_stall_detection(self):
        """Test current-based stall detection."""
        # First reading - high current starts
        self.mock_bus.sync_read.side_effect = [
            {"motor1": 30.0, "motor2": 30.0},  # Temperature
            {"motor1": 900, "motor2": 200},    # High current on motor1
            {"motor1": 50, "motor2": 0},       # Position
        ]
        
        self.monitor._perform_safety_checks()
        state1 = self.monitor.motor_states["motor1"]
        self.assertIsNotNone(state1.high_current_start_time)
        self.assertFalse(state1.is_stalled)
        
        # Second reading after stall duration - stall detected
        time.sleep(0.6)  # Wait longer than stall duration
        
        self.mock_bus.sync_read.side_effect = [
            {"motor1": 30.0, "motor2": 30.0},  # Temperature
            {"motor1": 900, "motor2": 200},    # Still high current
            {"motor1": 50, "motor2": 0},       # Position
        ]
        
        self.monitor._perform_safety_checks()
        self.assertTrue(state1.is_stalled)
        self.mock_bus.disable_torque.assert_called_with("motor1")

    def test_current_spike_detection(self):
        """Test current spike detection."""
        # Mock current spike
        self.mock_bus.sync_read.side_effect = [
            {"motor1": 30.0, "motor2": 30.0},  # Temperature
            {"motor1": 1300, "motor2": 200},   # Spike on motor1
            {"motor1": 50, "motor2": 0},       # Position
        ]
        
        self.monitor._perform_safety_checks()
        
        # Check torque reduction was applied
        self.mock_bus.read.assert_called()

    def test_position_limit_warning(self):
        """Test position limit proximity warning."""
        # Mock position near limit
        self.mock_bus.sync_read.side_effect = [
            {"motor1": 30.0, "motor2": 30.0},  # Temperature
            {"motor1": 500, "motor2": 200},    # Current
            {"motor1": 97, "motor2": 0},       # motor1 near max limit
        ]
        
        self.monitor._perform_safety_checks()
        
        # Check velocity reduction was applied
        self.mock_bus.write.assert_called()

    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        # Trigger emergency stop
        self.monitor.emergency_stop()
        
        self.assertTrue(self.monitor.emergency_stop_active)
        self.assertEqual(self.monitor.status, SafetyStatus.EMERGENCY_STOP)
        self.mock_bus.disable_torque.assert_called()
        self.assertEqual(self.monitor.stats["emergency_stops"], 1)

    def test_emergency_stop_reset(self):
        """Test emergency stop reset."""
        # Trigger emergency stop
        self.monitor.emergency_stop()
        self.assertTrue(self.monitor.emergency_stop_active)
        
        # Set safe temperatures
        for state in self.monitor.motor_states.values():
            state.temperature = 30.0
        
        # Reset emergency stop
        self.monitor.reset_emergency_stop()
        self.assertFalse(self.monitor.emergency_stop_active)

    def test_emergency_stop_reset_blocked(self):
        """Test emergency stop reset blocked by high temperature."""
        # Trigger emergency stop
        self.monitor.emergency_stop()
        
        # Set one motor with high temperature
        self.monitor.motor_states["motor1"].temperature = 40.0
        
        # Try to reset - should fail
        self.monitor.reset_emergency_stop()
        self.assertTrue(self.monitor.emergency_stop_active)

    def test_soft_start_trajectory(self):
        """Test soft start trajectory generation."""
        trajectory = self.monitor.apply_soft_start("motor1", 100.0, 0.0)
        
        # Check trajectory properties
        self.assertEqual(len(trajectory), self.monitor.thresholds.soft_start_steps)
        
        # Check smooth progression
        self.assertAlmostEqual(trajectory[0], 9.55, places=1)  # First step
        self.assertAlmostEqual(trajectory[-1], 100.0, places=1)  # Final position
        
        # Check monotonic increase
        for i in range(1, len(trajectory)):
            self.assertGreater(trajectory[i], trajectory[i-1])

    def test_safety_report(self):
        """Test safety report generation."""
        # Set some test states
        self.monitor.motor_states["motor1"].temperature = 42.0
        self.monitor.motor_states["motor1"].max_temp_reached = 44.0
        self.monitor.motor_states["motor1"].current = 600.0
        self.monitor.stats["total_violations"] = 5
        
        report = self.monitor.get_safety_report()
        
        # Check report structure
        self.assertIn("status", report)
        self.assertIn("emergency_stop", report)
        self.assertIn("statistics", report)
        self.assertIn("motors", report)
        
        # Check motor details
        motor1_report = report["motors"]["motor1"]
        self.assertEqual(motor1_report["temperature"], 42.0)
        self.assertEqual(motor1_report["max_temp"], 44.0)
        self.assertEqual(motor1_report["current"], 600.0)

    def test_context_manager(self):
        """Test context manager functionality."""
        with MotorSafetyMonitor(self.mock_bus) as monitor:
            self.assertTrue(monitor.monitoring_active)
        
        # Should be stopped after exiting context
        self.assertFalse(monitor.monitoring_active)

    def test_callback_invocation(self):
        """Test safety event callback."""
        callback = MagicMock()
        monitor = MotorSafetyMonitor(self.mock_bus, callback=callback)
        
        # Trigger emergency stop
        monitor.emergency_stop()
        
        # Check callback was called
        callback.assert_called_with("emergency_stop", None, None)

    def test_statistics_tracking(self):
        """Test statistics tracking."""
        # Simulate some violations
        self.monitor._record_violation(
            "motor1",
            SafetyViolationType.TEMPERATURE_WARNING,
            {"temperature": 42.0}
        )
        self.monitor._record_violation(
            "motor1",
            SafetyViolationType.CURRENT_STALL,
            {"current": 900}
        )
        
        # Check statistics
        self.assertEqual(self.monitor.stats["total_violations"], 2)
        self.assertEqual(self.monitor.stats["temperature_warnings"], 1)
        self.assertEqual(self.monitor.stats["current_stalls"], 1)

    def test_violation_history(self):
        """Test violation history tracking."""
        # Record a violation
        self.monitor._record_violation(
            "motor1",
            SafetyViolationType.TEMPERATURE_WARNING,
            {"temperature": 42.0}
        )
        
        state = self.monitor.motor_states["motor1"]
        self.assertEqual(len(state.violations), 1)
        self.assertIsNotNone(state.last_violation_time)
        
        violation = state.violations[0]
        self.assertEqual(violation["type"], SafetyViolationType.TEMPERATURE_WARNING)
        self.assertEqual(violation["data"]["temperature"], 42.0)


class TestIntegrationWithSO101(unittest.TestCase):
    """Integration tests with SO101 robot."""

    @patch('lerobot.motors.feetech.FeetechMotorsBus')
    @patch('lerobot.cameras.utils.make_cameras_from_configs')
    def test_so101_with_safety_enabled(self, mock_cameras, mock_bus_class):
        """Test SO101 with safety monitoring enabled."""
        from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
        
        # Create config with safety enabled
        config = SO101FollowerConfig(
            port="/dev/ttyUSB0",
            enable_safety_monitoring=True,
            temperature_warning=38.0,
            temperature_critical=43.0,
        )
        
        # Mock bus instance
        mock_bus = MagicMock()
        mock_bus.motors = {"motor1": MagicMock()}
        mock_bus.is_connected = True
        mock_bus.is_calibrated = True
        mock_bus_class.return_value = mock_bus
        
        # Mock cameras
        mock_cameras.return_value = {}
        
        # Create robot
        robot = SO101Follower(config)
        
        # Check safety monitor was created
        self.assertIsNotNone(robot.safety_monitor)
        self.assertEqual(robot.safety_monitor.thresholds.temperature_warning, 38.0)
        self.assertEqual(robot.safety_monitor.thresholds.temperature_critical, 43.0)

    @patch('lerobot.motors.feetech.FeetechMotorsBus')
    @patch('lerobot.cameras.utils.make_cameras_from_configs')
    def test_so101_emergency_stop(self, mock_cameras, mock_bus_class):
        """Test SO101 emergency stop functionality."""
        from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
        
        config = SO101FollowerConfig(
            port="/dev/ttyUSB0",
            enable_safety_monitoring=True,
        )
        
        # Mock bus
        mock_bus = MagicMock()
        mock_bus.motors = {"motor1": MagicMock()}
        mock_bus_class.return_value = mock_bus
        mock_cameras.return_value = {}
        
        # Create robot
        robot = SO101Follower(config)
        
        # Trigger emergency stop
        robot.emergency_stop()
        
        # Check motors were disabled
        mock_bus.disable_torque.assert_called()


if __name__ == "__main__":
    unittest.main()