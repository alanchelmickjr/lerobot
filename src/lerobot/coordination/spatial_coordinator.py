"""
Spatial Coordinator

Manages spatial relationships between coordinated arms including collision avoidance,
relative positioning, and workspace optimization.
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class SpatialCoordinator:
    """Manages spatial relationships between coordinated arms"""

    def __init__(self, baseline_separation: float = 0.3):
        """
        Initialize spatial coordinator

        Args:
            baseline_separation: Default separation between arms (meters)
        """
        self.baseline_separation = baseline_separation
        self.workspace_bounds = np.array([
            [-0.5, -0.5, 0.0],  # min x, y, z
            [0.5, 0.5, 0.8]     # max x, y, z
        ])

    def maintain_relative_position(self, leader_pos: np.ndarray,
                                 offset: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Maintain fixed offset between arms

        Args:
            leader_pos: Leader arm position [x, y, z]
            offset: Custom offset vector [dx, dy, dz]. If None, uses baseline_separation

        Returns:
            Follower position maintaining relative offset
        """
        if offset is None:
            offset = np.array([self.baseline_separation, 0, 0])

        return leader_pos + offset

    def avoid_collision(self, left_target: np.ndarray,
                       right_target: np.ndarray,
                       min_distance: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ensure arms don't collide during coordinated movement

        Args:
            left_target: Left arm target position
            right_target: Right arm target position
            min_distance: Minimum safe distance between arms

        Returns:
            Adjusted positions that avoid collision
        """
        left_adjusted = left_target.copy()
        right_adjusted = right_target.copy()

        current_distance = np.linalg.norm(left_target - right_target)

        if current_distance < min_distance:
            # Calculate adjustment needed
            adjustment_vector = (right_target - left_target) / current_distance
            adjustment_magnitude = (min_distance - current_distance) / 2

            # Move arms apart equally
            left_adjusted -= adjustment_vector * adjustment_magnitude
            right_adjusted += adjustment_vector * adjustment_magnitude

            logger.warning(".3f"
                         ".3f")

        return left_adjusted, right_adjusted

    def optimize_workspace_usage(self, leader_action: Dict) -> Dict:
        """
        Optimize arm positions for workspace coverage

        Args:
            leader_action: Leader action dictionary

        Returns:
            Optimized coordinated actions
        """
        # Extract position data (placeholder for kinematic integration)
        leader_pos = self._extract_position_from_action(leader_action)

        if leader_pos is None:
            # No position data available, return as-is
            return self._create_mirror_actions(leader_action)

        # Calculate optimal follower positions
        left_follower_pos = self.maintain_relative_position(
            leader_pos, offset=np.array([-self.baseline_separation/2, 0, 0])
        )
        right_follower_pos = self.maintain_relative_position(
            leader_pos, offset=np.array([self.baseline_separation/2, 0, 0])
        )

        # Ensure collision avoidance
        left_adjusted, right_adjusted = self.avoid_collision(
            left_follower_pos, right_follower_pos
        )

        # Check workspace bounds and adjust if necessary
        left_adjusted = self._clamp_to_workspace(left_adjusted)
        right_adjusted = self._clamp_to_workspace(right_adjusted)

        # Create action dictionary with adjusted positions
        return self._create_adjusted_actions(leader_action, left_adjusted, right_adjusted)

    def compute_relative_transform(self, leader_pose: np.ndarray,
                                 follower_pose: np.ndarray) -> np.ndarray:
        """
        Compute relative transformation between leader and follower

        Args:
            leader_pose: Leader pose (position + orientation)
            follower_pose: Follower pose (position + orientation)

        Returns:
            Relative transform vector
        """
        return follower_pose - leader_pose

    def validate_spatial_constraints(self, left_pos: np.ndarray,
                                   right_pos: np.ndarray) -> Dict:
        """
        Validate spatial constraints for coordinated movement

        Args:
            left_pos: Left arm position
            right_pos: Right arm position

        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'issues': [],
            'distance': np.linalg.norm(left_pos - right_pos)
        }

        # Check minimum distance
        if results['distance'] < 0.05:  # 5cm minimum
            results['valid'] = False
            results['issues'].append('Arms too close')

        # Check workspace bounds
        if not self._is_in_workspace(left_pos):
            results['valid'] = False
            results['issues'].append('Left arm out of workspace')

        if not self._is_in_workspace(right_pos):
            results['valid'] = False
            results['issues'].append('Right arm out of workspace')

        # Check for singularities (placeholder)
        # In full implementation, would check joint limits and singularities

        return results

    def _extract_position_from_action(self, action: Dict) -> Optional[np.ndarray]:
        """Extract position from action dictionary (placeholder)"""
        # This would integrate with actual kinematic data in full implementation
        return None

    def _create_mirror_actions(self, leader_action: Dict) -> Dict:
        """Create mirrored actions for both followers"""
        actions = {}

        for key, value in leader_action.items():
            if key.startswith('left_'):
                # Send to left follower
                actions[key] = value
                # Mirror to right follower
                right_key = key.replace('left_', 'right_')
                actions[right_key] = value

        return actions

    def _create_adjusted_actions(self, leader_action: Dict,
                               left_pos: np.ndarray, right_pos: np.ndarray) -> Dict:
        """Create action dictionary with adjusted positions (placeholder)"""
        # In full implementation, would properly encode positions back into action format
        # For now, return mirrored actions
        return self._create_mirror_actions(leader_action)

    def _clamp_to_workspace(self, position: np.ndarray) -> np.ndarray:
        """Clamp position to workspace bounds"""
        return np.clip(position,
                      self.workspace_bounds[0],
                      self.workspace_bounds[1])

    def _is_in_workspace(self, position: np.ndarray) -> bool:
        """Check if position is within workspace bounds"""
        return np.all(position >= self.workspace_bounds[0]) and \
               np.all(position <= self.workspace_bounds[1])