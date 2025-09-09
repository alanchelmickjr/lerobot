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

from dataclasses import dataclass, field
from typing import Optional

from lerobot.cameras import CameraConfig
from lerobot.motors.motor_safety import SafetyThresholds

from ..config import RobotConfig


@RobotConfig.register_subclass("so101_follower")
@dataclass
class SO101FollowerConfig(RobotConfig):
    # Port to connect to the arm
    port: str

    disable_torque_on_disconnect: bool = True

    # `max_relative_target` limits the magnitude of the relative positional target vector for safety purposes.
    # Set this to a positive scalar to have the same value for all motors, or a list that is the same length as
    # the number of motors in your follower arms.
    max_relative_target: int | None = None

    # cameras
    cameras: dict[str, CameraConfig] = field(default_factory=dict)

    # Set to `True` for backward compatibility with previous policies/dataset
    use_degrees: bool = False

    # Safety configuration - ENABLED with optimized polling frequency
    # Reduced frequency from 10Hz to 2Hz to avoid performance impact
    enable_safety_monitoring: bool = True
    safety_thresholds: Optional[SafetyThresholds] = None
    
    # Safety parameters (used if safety_thresholds is None)
    temperature_warning: float = 40.0  # °C
    temperature_critical: float = 45.0  # °C
    temperature_shutdown: float = 50.0  # °C
    current_stall_threshold: float = 800.0  # mA
    current_stall_duration: float = 0.5  # seconds
    soft_start_duration: float = 1.0  # seconds
    monitor_frequency: float = 2.0  # Hz - Reduced from 10Hz for smoother operation
    
    # Collision detection configuration - ENABLED for intelligent obstacle handling
    enable_collision_detection: bool = True
    collision_torque_threshold: float = 0.3  # Normalized torque (0-1)
    collision_current_threshold: float = 900.0  # mA - sustained current indicating collision
    collision_duration: float = 0.3  # seconds - how long force must be sustained
    collision_backoff_distance: float = 0.1  # Normalized units - how far to back off
    collision_max_retries: int = 3  # Max attempts before aborting movement
    
    # Auto-recalibration triggers
    auto_recalibrate_on_collisions: int = 5  # Recalibrate after this many collisions
    auto_recalibrate_time_hours: float = 1.0  # Recalibrate after this many hours
