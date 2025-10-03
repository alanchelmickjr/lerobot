"""
Coordination Safety Monitor

Provides safety monitoring for coordinated bimanual operations including
collision detection, workspace validation, and emergency stop functionality.
"""

import numpy as np
import logging
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CollisionBox:
    """Represents a 3D collision bounding box"""
    center: np.ndarray  # [x, y, z]
    size: np.ndarray    # [width, height, depth]
    orientation: float = 0.0  # rotation around Z axis


class CollisionDetector:
    """Basic collision detection for coordinated bimanual operations"""

    def __init__(self, safety_margin: float = 0.05):
        """
        Initialize collision detector

        Args:
            safety_margin: Minimum safe distance between arms (meters)
        """
        self.safety_margin = safety_margin
        self.workspace_bounds = np.array([
            [-0.5, -0.5, 0.0],  # min x, y, z
            [0.5, 0.5, 0.8]     # max x, y, z
        ])

    def check_arm_collision(self, left_position: np.ndarray,
                           right_position: np.ndarray) -> Tuple[bool, float]:
        """
        Check for collision between left and right arm end-effectors

        Args:
            left_position: Left arm position [x, y, z]
            right_position: Right arm position [x, y, z]

        Returns:
            Tuple of (collision_detected, distance)
        """
        distance = np.linalg.norm(left_position - right_position)

        # Simple sphere collision check
        collision_detected = distance < (2 * self.safety_margin)

        return collision_detected, distance

    def check_workspace_bounds(self, position: np.ndarray) -> bool:
        """
        Check if position is within workspace bounds

        Args:
            position: Position to check [x, y, z]

        Returns:
            True if within bounds, False otherwise
        """
        return np.all(position >= self.workspace_bounds[0]) and \
               np.all(position <= self.workspace_bounds[1])

    def validate_coordinated_trajectory(self, left_trajectory: List[np.ndarray],
                                       right_trajectory: List[np.ndarray]) -> Dict:
        """
        Validate a coordinated trajectory for safety

        Args:
            left_trajectory: List of left arm positions
            right_trajectory: List of right arm positions

        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'collision_points': [],
            'out_of_bounds_points': [],
            'min_distance': float('inf')
        }

        for i, (left_pos, right_pos) in enumerate(zip(left_trajectory, right_trajectory)):
            # Check collision
            collision, distance = self.check_arm_collision(left_pos, right_pos)
            results['min_distance'] = min(results['min_distance'], distance)

            if collision:
                results['collision_points'].append(i)
                results['valid'] = False

            # Check workspace bounds
            if not self.check_workspace_bounds(left_pos):
                results['out_of_bounds_points'].append(('left', i))

            if not self.check_workspace_bounds(right_pos):
                results['out_of_bounds_points'].append(('right', i))

        if results['out_of_bounds_points']:
            results['valid'] = False

        return results


class CoordinationSafetyMonitor:
    """Safety monitoring for coordinated bimanual operations"""

    def __init__(self):
        self.collision_detector = CollisionDetector()
        self.force_limits = {
            'max_force': 50.0,  # Newtons
            'max_torque': 10.0  # Newton-meters
        }
        self.emergency_stop_triggered = False

    def validate_coordinated_action(self, left_action: Dict,
                                   right_action: Dict) -> Tuple[bool, List[str]]:
        """
        Validate coordinated actions for safety

        Args:
            left_action: Left arm action dictionary
            right_action: Right arm action dictionary

        Returns:
            Tuple of (is_safe, list_of_warnings)
        """
        warnings = []

        # Extract positions if available (placeholder for future kinematic integration)
        left_pos = self._extract_position_from_action(left_action)
        right_pos = self._extract_position_from_action(right_action)

        if left_pos is not None and right_pos is not None:
            # Check collision
            collision, distance = self.collision_detector.check_arm_collision(left_pos, right_pos)
            if collision:
                warnings.append(f"Arm collision detected (distance: {distance:.3f}m)")
                return False, warnings

            # Check workspace bounds
            if not self.collision_detector.check_workspace_bounds(left_pos):
                warnings.append("Left arm outside workspace bounds")
                return False, warnings

            if not self.collision_detector.check_workspace_bounds(right_pos):
                warnings.append("Right arm outside workspace bounds")
                return False, warnings

        # Check force/torque limits (placeholder)
        if self._check_force_limits(left_action):
            warnings.append("Left arm force limit exceeded")

        if self._check_force_limits(right_action):
            warnings.append("Right arm force limit exceeded")

        is_safe = len(warnings) == 0
        return is_safe, warnings

    def emergency_stop_coordination(self) -> None:
        """Trigger emergency stop for coordinated operations"""
        logger.warning("Emergency stop triggered for coordinated bimanual operations")
        self.emergency_stop_triggered = True

    def reset_emergency_stop(self) -> None:
        """Reset emergency stop state"""
        self.emergency_stop_triggered = False

    def is_emergency_stop_active(self) -> bool:
        """Check if emergency stop is active"""
        return self.emergency_stop_triggered

    def _extract_position_from_action(self, action: Dict) -> Optional[np.ndarray]:
        """Extract position from action dictionary (placeholder)"""
        # This would integrate with actual kinematic data in full implementation
        # For now, return None to indicate position data not available
        return None

    def _check_force_limits(self, action: Dict) -> bool:
        """Check if action exceeds force/torque limits (placeholder)"""
        # This would check actual force/torque values in full implementation
        # For now, always return False (no violation)
        return False