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

from dataclasses import dataclass
from typing import Optional

from ..config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("bi_so100_leader")
@dataclass
class BiSO100LeaderConfig(TeleoperatorConfig):
    left_arm_port: str
    right_arm_port: Optional[str] = None

    def __post_init__(self):
        """Validate that left and right ports are different"""
        if self.right_arm_port is not None and self.left_arm_port == self.right_arm_port:
            raise ValueError(
                f"left_arm_port and right_arm_port cannot be the same. "
                f"Both are set to: {self.left_arm_port}. "
                f"Each arm requires its own distinct serial port to prevent EOF errors and connection failures."
            )
