"""DepthAI (OAK) camera support for LeRobot."""

from .camera_depthai import DepthAICamera
from .configuration_depthai import DepthAICameraConfig

__all__ = ["DepthAICamera", "DepthAICameraConfig"]