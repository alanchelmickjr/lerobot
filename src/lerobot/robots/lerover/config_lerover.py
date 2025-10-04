# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
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

from lerobot.cameras.configs import CameraConfig
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig

from ..config import RobotConfig


def lerover_cameras_config() -> dict[str, CameraConfig]:
    return {
        "front": OpenCVCameraConfig(
            index_or_path="/dev/video0", fps=30, width=1920, height=1080, rotation=0  # 1080p front camera
        ),
        "wrist": OpenCVCameraConfig(
            index_or_path="/dev/video2", fps=30, width=2048, height=1536, rotation=90  # 2K wrist camera
        ),
    }


@dataclass
class LeRoverAutonomyConfig:
    """Configuration for autonomous operation"""
    # AI Inference settings
    enable_ai_inference: bool = True
    raspi_ip: str = "192.168.1.100"  # Raspberry Pi IP address
    raspi_port: int = 8888  # Port for AI inference communication

    # SmolVLM settings
    smolvlm_model_path: str = "/path/to/smolvlm/model"  # Local path to SmolVLM model
    smolvlm_device: str = "cpu"  # Device for SmolVLM inference (cpu/cuda)

    # Autonomy settings
    autonomy_enabled: bool = False  # Master switch for autonomous operation
    max_autonomous_time_s: int = 300  # Maximum time for autonomous operation
    safety_timeout_ms: int = 1000  # Safety timeout for autonomous actions

    # Vision settings
    vision_fps: int = 10  # Vision processing frame rate
    confidence_threshold: float = 0.7  # Minimum confidence for AI decisions

    # ALOHA policy settings (if used)
    use_aloha_policy: bool = False
    aloha_model_path: str = "/path/to/aloha/policy"

    # Navigation settings
    obstacle_detection_distance_m: float = 0.5  # Minimum safe distance from obstacles
    navigation_speed_mps: float = 0.2  # Autonomous navigation speed


@RobotConfig.register_subclass("lerover")
@dataclass
class LeRoverConfig(RobotConfig):
    port: str = "/dev/ttyACM0"  # port to connect to the bus

    disable_torque_on_disconnect: bool = True

    # `max_relative_target` limits the magnitude of the relative positional target vector for safety purposes.
    # Set this to a positive scalar to have the same value for all motors, or a list that is the same length as
    # the number of motors in your follower arms.
    max_relative_target: int | None = None

    cameras: dict[str, CameraConfig] = field(default_factory=lerover_cameras_config)

    # Set to `True` for backward compatibility with previous policies/dataset
    use_degrees: bool = False

    # Autonomy configuration
    autonomy: LeRoverAutonomyConfig = field(default_factory=LeRoverAutonomyConfig)


@dataclass
class LeRoverHostConfig:
    # Network Configuration
    port_zmq_cmd: int = 5555
    port_zmq_observations: int = 5556

    # Duration of the application
    connection_time_s: int = 300  # Longer default for autonomous operation

    # Watchdog: stop the robot if no command is received for over 0.5 seconds.
    watchdog_timeout_ms: int = 500

    # If robot jitters decrease the frequency and monitor cpu load with `top` in cmd
    max_loop_freq_hz: int = 30


@RobotConfig.register_subclass("lerover_client")
@dataclass
class LeRoverClientConfig(RobotConfig):
    # Network Configuration
    remote_ip: str
    port_zmq_cmd: int = 5555
    port_zmq_observations: int = 5556

    teleop_keys: dict[str, str] = field(
        default_factory=lambda: {
            # Movement
            "forward": "w",
            "backward": "s",
            "left": "a",
            "right": "d",
            "rotate_left": "z",
            "rotate_right": "x",
            # Speed control
            "speed_up": "r",
            "speed_down": "f",
            # Autonomy control
            "toggle_autonomy": "t",
            "emergency_stop": "e",
            # quit teleop
            "quit": "q",
        }
    )

    cameras: dict[str, CameraConfig] = field(default_factory=lerover_cameras_config)

    polling_timeout_ms: int = 15
    connect_timeout_s: int = 5

    # Autonomy configuration
    autonomy: LeRoverAutonomyConfig = field(default_factory=LeRoverAutonomyConfig)