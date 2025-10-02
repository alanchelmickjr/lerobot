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

"""
Provides the DepthAICamera class for capturing frames from DepthAI (OAK) cameras.
"""

import logging
import time
from threading import Event, Lock, Thread
from typing import Any

import cv2
import numpy as np

try:
    import depthai as dai
except Exception as e:
    logging.info(f"Could not import depthai: {e}")

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..camera import Camera
from ..configs import ColorMode
from ..utils import get_cv2_rotation
from .configuration_depthai import DepthAICameraConfig

logger = logging.getLogger(__name__)


class DepthAICamera(Camera):
    """
    Manages interactions with DepthAI (OAK) cameras for frame and depth recording.

    This class provides an interface for OAK cameras using the DepthAI library.
    It supports auto-detection or specific device targeting via MxId or IP address.
    It also supports capturing depth maps alongside color frames.

    Use the provided utility script to find available cameras:
    ```bash
    lerobot-find-cameras depthai
    ```

    A `DepthAICamera` instance can use auto-detection or specify a device ID.
    The camera's default settings are used unless overridden in the configuration.

    Example:
        ```python
        from lerobot.cameras.depthai import DepthAICamera, DepthAICameraConfig
        from lerobot.cameras import ColorMode, Cv2Rotation

        # Basic usage with auto-detection
        config = DepthAICameraConfig(device_id="auto")
        camera = DepthAICamera(config)
        camera.connect()

        # Read 1 frame synchronously
        color_image = camera.read()
        print(color_image.shape)

        # Read 1 frame asynchronously
        async_image = camera.async_read()

        # When done, properly disconnect the camera
        camera.disconnect()

        # Example with depth capture and custom settings
        custom_config = DepthAICameraConfig(
            device_id="auto",
            fps=30,
            width=1280,
            height=720,
            color_mode=ColorMode.BGR,
            rotation=Cv2Rotation.NO_ROTATION,
            use_depth=True
        )
        depth_camera = DepthAICamera(custom_config)
        depth_camera.connect()

        # Read 1 depth frame
        depth_map = depth_camera.read_depth()
        ```
    """

    def __init__(self, config: DepthAICameraConfig):
        """
        Initializes the DepthAICamera instance.

        Args:
            config: The configuration settings for the camera.
        """
        super().__init__(config)

        self.config = config
        self.device_id = config.device_id

        self.fps = config.fps
        self.color_mode = config.color_mode
        self.use_depth = config.use_depth
        self.warmup_s = config.warmup_s

        self.pipeline: dai.Pipeline | None = None
        self.device: dai.Device | None = None
        self.color_queue: dai.DataOutputQueue | None = None
        self.depth_queue: dai.DataOutputQueue | None = None

        self.thread: Thread | None = None
        self.stop_event: Event | None = None
        self.frame_lock: Lock = Lock()
        self.latest_frame: np.ndarray | None = None
        self.new_frame_event: Event = Event()

        self.rotation: int | None = get_cv2_rotation(config.rotation)

        if self.height and self.width:
            self.capture_width, self.capture_height = self.width, self.height
            if self.rotation in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]:
                self.capture_width, self.capture_height = self.height, self.width

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.device_id})"

    @property
    def is_connected(self) -> bool:
        """Checks if the camera device is connected and pipeline is running."""
        return self.device is not None and self.pipeline is not None

    def connect(self, warmup: bool = True):
        """
        Connects to the DepthAI camera specified in the configuration.

        Initializes the DepthAI pipeline, configures the required streams (color
        and optionally depth), starts the pipeline, and validates the settings.

        Raises:
            DeviceAlreadyConnectedError: If the camera is already connected.
            ConnectionError: If the camera fails to connect or no devices are found.
        """
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} is already connected.")

        # Create pipeline
        self.pipeline = dai.Pipeline()
        
        # Create camera node and build it FIRST (required in DepthAI v3.0)
        camera = self.pipeline.create(dai.node.Camera)
        camera.build()  # Must build before requesting outputs
        
        # Use width/height from config or defaults
        width = self.width or 640
        height = self.height or 480
        
        # Request RGB output with size tuple (v3.0 API)
        rgb_output = camera.requestOutput((width, height))
        
        # Note: FPS is handled differently in v3.0 - set via pipeline or device config
        # camera.setFps() method doesn't exist in v3.0 Camera node

        # Create BenchmarkOut node for color (XLinkOut doesn't exist in v3.0)
        color_out = self.pipeline.create(dai.node.BenchmarkOut)
        rgb_output.link(color_out.input)

        # Add depth if enabled
        if self.use_depth:
            # Request depth output with size tuple
            depth_output = camera.requestOutput((width, height))
            
            # Create BenchmarkOut for depth
            depth_out = self.pipeline.create(dai.node.BenchmarkOut)
            depth_output.link(depth_out.input)

        try:
            # Create device first, then start pipeline (v3.0 API change)
            if self.device_id == "auto":
                self.device = dai.Device()
            else:
                # Try to connect to specific device by ID/IP
                device_info = dai.DeviceInfo(self.device_id)
                self.device = dai.Device(device_info)
            
            # Start pipeline on device
            self.device.startPipeline(self.pipeline)
                
            # Get output queues using BenchmarkOut queue names
            self.color_queue = self.device.getOutputQueue(name="benchmark_out", maxSize=4, blocking=False)
            if self.use_depth:
                # For depth, we need a different queue name or instance
                self.depth_queue = self.device.getOutputQueue(name="benchmark_out_1", maxSize=4, blocking=False)
                
        except Exception as e:
            self.pipeline = None
            self.device = None
            raise ConnectionError(
                f"Failed to open {self}. Run `lerobot-find-cameras depthai` to find available cameras."
            ) from e

        # Configure capture settings if not specified
        self._configure_capture_settings()

        if warmup:
            start_time = time.time()
            while time.time() - start_time < self.warmup_s:
                self.read()
                time.sleep(0.1)

        logger.info(f"{self} connected.")

    @staticmethod
    def find_cameras() -> list[dict[str, Any]]:
        """
        Detects available DepthAI cameras connected to the system.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with camera information.
        """
        found_cameras_info = []
        
        try:
            devices = dai.Device.getAllAvailableDevices()
            
            for device_info in devices:
                camera_info = {
                    "name": device_info.name,
                    "type": "DepthAI",
                    "id": device_info.getDeviceId(),
                    "state": device_info.state.name,
                    "protocol": device_info.protocol.name,
                    "platform": device_info.platform.name,
                }
                
                # Add default stream profile
                camera_info["default_stream_profile"] = {
                    "format": "RGB",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                }
                
                found_cameras_info.append(camera_info)
                
        except Exception as e:
            logger.warning(f"Error detecting DepthAI cameras: {e}")
            
        return found_cameras_info

    def _configure_capture_settings(self) -> None:
        """Sets fps, width, and height if not already configured."""
        if not self.is_connected:
            raise DeviceNotConnectedError(f"Cannot validate settings for {self} as it is not connected.")

        # Use defaults if not specified
        if self.fps is None:
            self.fps = 30

        if self.width is None or self.height is None:
            # Default preview size
            actual_width, actual_height = 416, 416  # DepthAI default preview size
            if self.rotation in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]:
                self.width, self.height = actual_height, actual_width
                self.capture_width, self.capture_height = actual_width, actual_height
            else:
                self.width, self.height = actual_width, actual_height
                self.capture_width, self.capture_height = actual_width, actual_height

    def read_depth(self, timeout_ms: int = 200) -> np.ndarray:
        """
        Reads a single depth frame synchronously from the camera.

        Args:
            timeout_ms (int): Maximum time in milliseconds to wait for a frame.

        Returns:
            np.ndarray: The depth map as a NumPy array (height, width) of type uint16.

        Raises:
            DeviceNotConnectedError: If the camera is not connected.
            RuntimeError: If depth is not enabled or reading fails.
        """
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")
        if not self.use_depth:
            raise RuntimeError(
                f"Failed to capture depth frame. Depth stream is not enabled for {self}."
            )

        start_time = time.perf_counter()

        in_depth = self.depth_queue.get()
        if in_depth is None:
            raise RuntimeError(f"{self} read_depth failed - no frame available.")

        depth_frame = in_depth.getFrame()
        depth_map_processed = self._postprocess_image(depth_frame, depth_frame=True)

        read_duration_ms = (time.perf_counter() - start_time) * 1e3
        logger.debug(f"{self} depth read took: {read_duration_ms:.1f}ms")

        return depth_map_processed

    def read(self, color_mode: ColorMode | None = None, timeout_ms: int = 200) -> np.ndarray:
        """
        Reads a single color frame synchronously from the camera.

        Args:
            color_mode: Optional color mode override.
            timeout_ms (int): Maximum time in milliseconds to wait for a frame.

        Returns:
            np.ndarray: The captured color frame as a NumPy array (height, width, channels).

        Raises:
            DeviceNotConnectedError: If the camera is not connected.
            RuntimeError: If reading the frame fails.
        """
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        start_time = time.perf_counter()

        in_rgb = self.color_queue.get()
        if in_rgb is None:
            raise RuntimeError(f"{self} read failed - no frame available.")

        color_frame = in_rgb.getCvFrame()
        color_image_processed = self._postprocess_image(color_frame, color_mode)

        read_duration_ms = (time.perf_counter() - start_time) * 1e3
        logger.debug(f"{self} read took: {read_duration_ms:.1f}ms")

        return color_image_processed

    def _postprocess_image(
        self, image: np.ndarray, color_mode: ColorMode | None = None, depth_frame: bool = False
    ) -> np.ndarray:
        """
        Applies color conversion, dimension validation, and rotation to a raw frame.

        Args:
            image: The raw image frame.
            color_mode: Optional color mode override.
            depth_frame: Whether this is a depth frame.

        Returns:
            np.ndarray: The processed image frame.
        """
        if color_mode and color_mode not in (ColorMode.RGB, ColorMode.BGR):
            raise ValueError(
                f"Invalid requested color mode '{color_mode}'. Expected {ColorMode.RGB} or {ColorMode.BGR}."
            )

        effective_color_mode = color_mode if color_mode is not None else self.color_mode

        if depth_frame:
            h, w = image.shape
        else:
            h, w, c = image.shape
            if c != 3:
                raise RuntimeError(f"{self} frame channels={c} do not match expected 3 channels (RGB/BGR).")

        processed_image = image
        
        # Apply color conversion if needed
        if not depth_frame and effective_color_mode == ColorMode.BGR:
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)

        # Apply rotation if specified
        if self.rotation in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]:
            processed_image = cv2.rotate(processed_image, self.rotation)

        return processed_image

    def _read_loop(self):
        """
        Internal loop run by the background thread for asynchronous reading.
        """
        while not self.stop_event.is_set():
            try:
                color_image = self.read(timeout_ms=500)

                with self.frame_lock:
                    self.latest_frame = color_image
                self.new_frame_event.set()

            except DeviceNotConnectedError:
                break
            except Exception as e:
                logger.warning(f"Error reading frame in background thread for {self}: {e}")

    def _start_read_thread(self) -> None:
        """Starts the background read thread if not running."""
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=0.1)
        if self.stop_event is not None:
            self.stop_event.set()

        self.stop_event = Event()
        self.thread = Thread(target=self._read_loop, args=(), name=f"{self}_read_loop")
        self.thread.daemon = True
        self.thread.start()

    def _stop_read_thread(self):
        """Signals the background read thread to stop and waits for it to join."""
        if self.stop_event is not None:
            self.stop_event.set()

        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        self.thread = None
        self.stop_event = None

    def async_read(self, timeout_ms: float = 200) -> np.ndarray:
        """
        Reads the latest available frame asynchronously.

        Args:
            timeout_ms: Maximum time in milliseconds to wait for a frame.

        Returns:
            np.ndarray: The latest captured frame.

        Raises:
            DeviceNotConnectedError: If the camera is not connected.
            TimeoutError: If no frame becomes available within timeout.
        """
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        if self.thread is None or not self.thread.is_alive():
            self._start_read_thread()

        if not self.new_frame_event.wait(timeout=timeout_ms / 1000.0):
            thread_alive = self.thread is not None and self.thread.is_alive()
            raise TimeoutError(
                f"Timed out waiting for frame from camera {self} after {timeout_ms} ms. "
                f"Read thread alive: {thread_alive}."
            )

        with self.frame_lock:
            frame = self.latest_frame
            self.new_frame_event.clear()

        if frame is None:
            raise RuntimeError(f"Internal error: Event set but no frame available for {self}.")

        return frame

    def disconnect(self):
        """
        Disconnects from the camera and cleans up resources.

        Raises:
            DeviceNotConnectedError: If the camera is already disconnected.
        """
        if not self.is_connected and self.thread is None:
            raise DeviceNotConnectedError(
                f"Attempted to disconnect {self}, but it appears already disconnected."
            )

        if self.thread is not None:
            self._stop_read_thread()

        if self.device is not None:
            self.device.close()
            self.device = None
            self.pipeline = None
            self.color_queue = None
            self.depth_queue = None

        logger.info(f"{self} disconnected.")