#!/usr/bin/env python

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

import json
import logging
import socket
import threading
import time
from functools import cached_property
from typing import Any

import numpy as np

from lerobot.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from .config_lerover import LeRoverConfig
from ..lekiwi.lekiwi import LeKiwi

logger = logging.getLogger(__name__)


class AIInferenceClient:
    """Client for communicating with AI inference server on Raspberry Pi"""

    def __init__(self, raspi_ip: str, raspi_port: int):
        self.raspi_ip = raspi_ip
        self.raspi_port = raspi_port
        self.socket = None
        self.connected = False

    def connect(self):
        """Connect to the AI inference server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.raspi_ip, self.raspi_port))
            self.connected = True
            logger.info(f"Connected to AI inference server at {self.raspi_ip}:{self.raspi_port}")
        except Exception as e:
            logger.error(f"Failed to connect to AI inference server: {e}")
            self.connected = False

    def disconnect(self):
        """Disconnect from the AI inference server"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False

    def send_inference_request(self, image_data: bytes, task_description: str) -> dict | None:
        """Send an inference request to the AI server"""
        if not self.connected:
            return None

        try:
            # Prepare request data
            request_data = {
                "task": task_description,
                "image_size": len(image_data),
            }

            # Send JSON header first
            header = json.dumps(request_data).encode('utf-8')
            header_size = len(header)
            self.socket.sendall(header_size.to_bytes(4, byteorder='big'))
            self.socket.sendall(header)

            # Send image data
            self.socket.sendall(image_data)

            # Receive response
            response_size_data = self.socket.recv(4)
            if len(response_size_data) != 4:
                return None

            response_size = int.from_bytes(response_size_data, byteorder='big')
            response_data = self.socket.recv(response_size)

            if len(response_data) != response_size:
                return None

            response = json.loads(response_data.decode('utf-8'))
            return response

        except Exception as e:
            logger.error(f"AI inference request failed: {e}")
            return None


class SmolVLMAgent:
    """Local SmolVLM agent for vision-language processing"""

    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.processor = None
        self.initialized = False

    def initialize(self):
        """Initialize the SmolVLM model"""
        try:
            from transformers import AutoProcessor, AutoModelForVision2Seq
            import torch

            self.processor = AutoProcessor.from_pretrained(self.model_path)
            self.model = AutoModelForVision2Seq.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            self.initialized = True
            logger.info(f"SmolVLM model initialized on {self.device}")
        except ImportError:
            logger.warning("Transformers not available, SmolVLM functionality disabled")
        except Exception as e:
            logger.error(f"Failed to initialize SmolVLM: {e}")

    def process_image(self, image: np.ndarray, task: str) -> str:
        """Process image with SmolVLM for the given task"""
        if not self.initialized:
            return "SmolVLM not initialized"

        try:
            import torch
            from PIL import Image

            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)

            # Prepare inputs
            inputs = self.processor(text=task, images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate response
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_length=50)
                generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            return generated_text.strip()

        except Exception as e:
            logger.error(f"SmolVLM processing failed: {e}")
            return "Processing failed"


class LeRover(LeKiwi):
    """
    Autonomous version of LeKiwi robot with AI inference capabilities.
    Extends LeKiwi with autonomy features including SmolVLM and remote AI inference.
    """

    config_class = LeRoverConfig
    name = "lerover"

    def __init__(self, config: LeRoverConfig):
        super().__init__(config)
        self.config = config
        self.autonomy_config = config.autonomy

        # AI components
        self.ai_client = None
        self.smolvlm_agent = None
        self.autonomy_thread = None
        self.autonomy_active = False
        self.emergency_stop = False

        # Initialize AI components if enabled
        if self.autonomy_config.enable_ai_inference:
            self.ai_client = AIInferenceClient(
                self.autonomy_config.raspi_ip,
                self.autonomy_config.raspi_port
            )

        if self.autonomy_config.smolvlm_model_path:
            self.smolvlm_agent = SmolVLMAgent(
                self.autonomy_config.smolvlm_model_path,
                self.autonomy_config.smolvlm_device
            )
            self.smolvlm_agent.initialize()

    def connect(self, calibrate: bool = True) -> None:
        super().connect(calibrate)

        # Connect AI inference client
        if self.ai_client:
            self.ai_client.connect()

    def disconnect(self):
        # Stop autonomy if active
        self.stop_autonomy()

        # Disconnect AI client
        if self.ai_client:
            self.ai_client.disconnect()

        super().disconnect()

    def start_autonomy(self, task_description: str = "Navigate autonomously and avoid obstacles"):
        """Start autonomous operation"""
        if self.autonomy_active:
            logger.warning("Autonomy already active")
            return

        if not self.is_connected:
            raise DeviceNotConnectedError("LeRover must be connected before starting autonomy")

        self.autonomy_active = True
        self.emergency_stop = False
        self.autonomy_thread = threading.Thread(
            target=self._autonomy_loop,
            args=(task_description,),
            daemon=True
        )
        self.autonomy_thread.start()
        logger.info("LeRover autonomy started")

    def stop_autonomy(self):
        """Stop autonomous operation"""
        self.autonomy_active = False
        self.emergency_stop = True

        if self.autonomy_thread and self.autonomy_thread.is_alive():
            self.autonomy_thread.join(timeout=2.0)

        # Stop the base
        self.stop_base()
        logger.info("LeRover autonomy stopped")

    def _autonomy_loop(self, task_description: str):
        """Main autonomy control loop"""
        start_time = time.time()
        last_vision_time = 0

        while self.autonomy_active and not self.emergency_stop:
            current_time = time.time()

            # Safety timeout check
            if current_time - start_time > self.autonomy_config.max_autonomous_time_s:
                logger.warning("Autonomous operation timeout reached")
                break

            # Vision processing at reduced rate
            if current_time - last_vision_time > (1.0 / self.autonomy_config.vision_fps):
                try:
                    action = self._compute_autonomous_action(task_description)
                    if action:
                        self.send_action(action)
                    last_vision_time = current_time
                except Exception as e:
                    logger.error(f"Autonomy action computation failed: {e}")
                    self.stop_base()

            time.sleep(0.1)  # Control loop rate ~10Hz

        self.stop_autonomy()

    def _compute_autonomous_action(self, task_description: str) -> dict[str, Any] | None:
        """Compute autonomous action based on current observations"""
        try:
            # Get current observation
            obs = self.get_observation()

            # Get front camera image for vision processing
            front_image = obs.get("front")
            if front_image is None:
                return None

            # Use SmolVLM for local vision-language processing
            if self.smolvlm_agent and self.smolvlm_agent.initialized:
                vision_description = self.smolvlm_agent.process_image(
                    front_image,
                    f"Describe what you see in this image for autonomous navigation: {task_description}"
                )
                logger.debug(f"SmolVLM vision: {vision_description}")

            # Use remote AI inference for decision making
            action = None
            if self.ai_client and self.ai_client.connected:
                # Encode image for transmission
                import cv2
                _, encoded_image = cv2.imencode('.jpg', front_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
                image_bytes = encoded_image.tobytes()

                # Send inference request
                response = self.ai_client.send_inference_request(image_bytes, task_description)
                if response:
                    action = self._parse_ai_response(response)

            # Fallback: simple obstacle avoidance if no AI available
            if action is None:
                action = self._simple_obstacle_avoidance(obs)

            return action

        except Exception as e:
            logger.error(f"Autonomous action computation error: {e}")
            return None

    def _parse_ai_response(self, response: dict) -> dict[str, Any] | None:
        """Parse AI inference response into robot actions"""
        try:
            # Expected response format from AI server
            # {"action": {"x.vel": 0.1, "y.vel": 0.0, "theta.vel": 0.0, ...}}
            action_data = response.get("action", {})

            # Validate action
            required_keys = ["x.vel", "y.vel", "theta.vel"]
            if not all(key in action_data for key in required_keys):
                logger.warning("AI response missing required action keys")
                return None

            # Scale velocities for safety
            for key in required_keys:
                action_data[key] = float(action_data[key]) * self.autonomy_config.navigation_speed_mps

            return action_data

        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None

    def _simple_obstacle_avoidance(self, obs: dict) -> dict[str, Any]:
        """Simple obstacle avoidance based on basic image processing"""
        # This is a placeholder for simple reactive obstacle avoidance
        # In a real implementation, you might use depth sensing or basic CV

        # Default: move forward slowly
        return {
            "x.vel": 0.1,
            "y.vel": 0.0,
            "theta.vel": 0.0,
            # Arm stays in current position
            "arm_shoulder_pan.pos": obs.get("arm_shoulder_pan.pos", 0.0),
            "arm_shoulder_lift.pos": obs.get("arm_shoulder_lift.pos", 0.0),
            "arm_elbow_flex.pos": obs.get("arm_elbow_flex.pos", 0.0),
            "arm_wrist_flex.pos": obs.get("arm_wrist_flex.pos", 0.0),
            "arm_wrist_roll.pos": obs.get("arm_wrist_roll.pos", 0.0),
            "arm_gripper.pos": obs.get("arm_gripper.pos", 0.0),
        }

    def emergency_stop_autonomy(self):
        """Emergency stop for autonomous operation"""
        logger.warning("Emergency stop activated!")
        self.emergency_stop = True
        self.stop_base()