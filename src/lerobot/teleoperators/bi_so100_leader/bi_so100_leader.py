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

import logging
from functools import cached_property

from lerobot.teleoperators.so100_leader.config_so100_leader import SO100LeaderConfig
from lerobot.teleoperators.so100_leader.so100_leader import SO100Leader

from ..teleoperator import Teleoperator
from .config_bi_so100_leader import BiSO100LeaderConfig

logger = logging.getLogger(__name__)


class BiSO100Leader(Teleoperator):
    """
    [Bimanual SO-100 Leader Arms](https://github.com/TheRobotStudio/SO-ARM100) designed by TheRobotStudio
    This bimanual leader arm can also be easily adapted to use SO-101 leader arms, just replace the SO100Leader class with SO101Leader and SO100LeaderConfig with SO101LeaderConfig.
    """

    config_class = BiSO100LeaderConfig
    name = "bi_so100_leader"

    def __init__(self, config: BiSO100LeaderConfig):
        super().__init__(config)
        self.config = config

        left_arm_config = SO100LeaderConfig(
            id=f"{config.id}_left" if config.id else None,
            calibration_dir=config.calibration_dir,
            port=config.left_arm_port,
        )

        self.left_arm = SO100Leader(left_arm_config)
        self.right_arm = None

        # Only create right arm if port is provided (for mirror mode compatibility)
        if config.right_arm_port is not None:
            right_arm_config = SO100LeaderConfig(
                id=f"{config.id}_right" if config.id else None,
                calibration_dir=config.calibration_dir,
                port=config.right_arm_port,
            )
            self.right_arm = SO100Leader(right_arm_config)

    @cached_property
    def action_features(self) -> dict[str, type]:
        features = {f"left_{motor}.pos": float for motor in self.left_arm.bus.motors}
        if self.right_arm is not None:
            features.update({f"right_{motor}.pos": float for motor in self.right_arm.bus.motors})
        return features

    @cached_property
    def feedback_features(self) -> dict[str, type]:
        return {}

    @property
    def is_connected(self) -> bool:
        left_connected = self.left_arm.is_connected
        right_connected = self.right_arm.is_connected if self.right_arm is not None else True
        return left_connected and right_connected

    def connect(self, calibrate: bool = True) -> None:
        self.left_arm.connect(calibrate)
        if self.right_arm is not None:
            self.right_arm.connect(calibrate)

    @property
    def is_calibrated(self) -> bool:
        left_calibrated = self.left_arm.is_calibrated
        right_calibrated = self.right_arm.is_calibrated if self.right_arm is not None else True
        return left_calibrated and right_calibrated

    def calibrate(self) -> None:
        self.left_arm.calibrate()
        if self.right_arm is not None:
            self.right_arm.calibrate()

    def configure(self) -> None:
        self.left_arm.configure()
        if self.right_arm is not None:
            self.right_arm.configure()

    def setup_motors(self) -> None:
        self.left_arm.setup_motors()
        if self.right_arm is not None:
            self.right_arm.setup_motors()

    def get_action(self) -> dict[str, float]:
        action_dict = {}

        # Add "left_" prefix
        left_action = self.left_arm.get_action()
        action_dict.update({f"left_{key}": value for key, value in left_action.items()})

        # Add "right_" prefix only if right arm exists
        if self.right_arm is not None:
            right_action = self.right_arm.get_action()
            action_dict.update({f"right_{key}": value for key, value in right_action.items()})

        return action_dict

    def send_feedback(self, feedback: dict[str, float]) -> None:
        # Remove "left_" prefix
        left_feedback = {
            key.removeprefix("left_"): value for key, value in feedback.items() if key.startswith("left_")
        }
        # Remove "right_" prefix
        right_feedback = {
            key.removeprefix("right_"): value for key, value in feedback.items() if key.startswith("right_")
        }

        if left_feedback:
            self.left_arm.send_feedback(left_feedback)
        if right_feedback and self.right_arm is not None:
            self.right_arm.send_feedback(right_feedback)

    def disconnect(self) -> None:
        self.left_arm.disconnect()
        if self.right_arm is not None:
            self.right_arm.disconnect()
