"""
Task-Aware Coordinator

Provides context-sensitive coordination based on task requirements.
Includes basic task detection from leader movements.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enumeration of supported task types"""
    GENERAL = "general"
    PICK_PLACE = "pick_place"
    ASSEMBLY = "assembly"
    TRANSPORT = "transport"
    SORTING = "sorting"
    PACKAGING = "packaging"


class TaskStrategy:
    """Base class for task-specific coordination strategies"""

    def __init__(self, name: str):
        self.name = name

    def compute_actions(self, leader_action: Dict) -> Dict:
        """Compute coordinated actions for this task type"""
        raise NotImplementedError

    def validate_task_context(self, trajectory: List[Dict]) -> bool:
        """Validate if trajectory matches this task type"""
        return False


class PickPlaceStrategy(TaskStrategy):
    """Strategy for pick-and-place operations"""

    def __init__(self):
        super().__init__("pick_place")

    def compute_actions(self, leader_action: Dict) -> Dict:
        """Coordinated pick-and-place with approach/grasp/lift phases"""
        # Basic implementation: mirror with slight offset for bimanual grasp
        actions = {}

        for key, value in leader_action.items():
            if key.startswith('left_'):
                # Left arm follows leader directly
                actions[key] = value
                # Right arm mirrors with small offset for grasping
                right_key = key.replace('left_', 'right_')
                if 'position' in key.lower():
                    # Add small offset for grasping
                    actions[right_key] = value + np.array([0.02, 0, 0])  # 2cm offset
                else:
                    actions[right_key] = value

        return actions


class AssemblyStrategy(TaskStrategy):
    """Strategy for assembly operations"""

    def __init__(self):
        super().__init__("assembly")

    def compute_actions(self, leader_action: Dict) -> Dict:
        """Assembly tasks with one arm holding, other manipulating"""
        # Basic implementation: left arm holds steady, right arm follows leader
        actions = {}

        # Right arm follows leader for manipulation
        for key, value in leader_action.items():
            if key.startswith('left_'):
                right_key = key.replace('left_', 'right_')
                actions[right_key] = value

        # Left arm holds position (would need state tracking in full implementation)
        # For now, mirror with reduced movement
        for key, value in leader_action.items():
            if key.startswith('left_'):
                actions[key] = value * 0.1  # Reduced movement for holding

        return actions


class TransportStrategy(TaskStrategy):
    """Strategy for transport operations"""

    def __init__(self):
        super().__init__("transport")

    def compute_actions(self, leader_action: Dict) -> Dict:
        """Synchronized movement for transporting objects"""
        # Basic implementation: synchronized movement with maintained grip
        actions = {}

        for key, value in leader_action.items():
            if key.startswith('left_'):
                # Both arms move in sync
                actions[key] = value
                right_key = key.replace('left_', 'right_')
                actions[right_key] = value

        return actions


class TaskAwareCoordinator:
    """Context-sensitive coordination based on task requirements"""

    def __init__(self):
        self.task_database = {
            TaskType.PICK_PLACE: PickPlaceStrategy(),
            TaskType.ASSEMBLY: AssemblyStrategy(),
            TaskType.TRANSPORT: TransportStrategy(),
        }
        self.current_task = TaskType.GENERAL
        self.trajectory_buffer = []
        self.buffer_size = 50

    def detect_task_context(self, leader_trajectory: List[Dict]) -> TaskType:
        """
        Automatically detect task type from leader movements

        Args:
            leader_trajectory: List of recent leader actions

        Returns:
            Detected task type
        """
        if len(leader_trajectory) < 10:
            return TaskType.GENERAL

        # Basic task detection based on movement patterns
        velocities = self._compute_velocities(leader_trajectory)

        if self._is_pick_place_pattern(velocities):
            return TaskType.PICK_PLACE
        elif self._is_assembly_pattern(velocities):
            return TaskType.ASSEMBLY
        elif self._is_transport_pattern(velocities):
            return TaskType.TRANSPORT
        else:
            return TaskType.GENERAL

    def adapt_coordination(self, task_type: TaskType, leader_action: Dict) -> Dict:
        """
        Adapt coordination strategy based on detected task

        Args:
            task_type: Detected task type
            leader_action: Current leader action

        Returns:
            Coordinated actions for both followers
        """
        strategy = self.task_database.get(task_type)
        if strategy:
            return strategy.compute_actions(leader_action)
        else:
            # Fallback to general coordination
            return self._general_coordination(leader_action)

    def update_trajectory_context(self, leader_action: Dict) -> None:
        """Update trajectory buffer for task detection"""
        self.trajectory_buffer.append(leader_action.copy())
        if len(self.trajectory_buffer) > self.buffer_size:
            self.trajectory_buffer.pop(0)

        # Update current task detection
        if len(self.trajectory_buffer) >= 10:
            self.current_task = self.detect_task_context(self.trajectory_buffer[-20:])  # Last 20 actions

    def get_current_task_context(self) -> TaskType:
        """Get currently detected task type"""
        return self.current_task

    def _compute_velocities(self, trajectory: List[Dict]) -> List[float]:
        """Compute movement velocities from trajectory"""
        velocities = []

        for i in range(1, len(trajectory)):
            prev_action = trajectory[i-1]
            curr_action = trajectory[i]

            # Simple velocity computation (placeholder)
            # In full implementation, would compute actual joint velocities
            velocity = 0.0
            for key in curr_action.keys():
                if key in prev_action and isinstance(curr_action[key], (int, float)):
                    velocity += abs(curr_action[key] - prev_action[key])

            velocities.append(velocity)

        return velocities

    def _is_pick_place_pattern(self, velocities: List[float]) -> bool:
        """Detect pick-place pattern: fast movements separated by pauses"""
        if len(velocities) < 5:
            return False

        # Look for high-low-high pattern (approach, grasp, lift)
        peaks = []
        for i in range(1, len(velocities)-1):
            if velocities[i-1] < velocities[i] > velocities[i+1]:
                peaks.append(i)

        return len(peaks) >= 2  # At least approach and lift phases

    def _is_assembly_pattern(self, velocities: List[float]) -> bool:
        """Detect assembly pattern: precise, slow movements"""
        if len(velocities) < 5:
            return False

        # Assembly typically has low, consistent velocities
        avg_velocity = np.mean(velocities)
        variance = np.var(velocities)

        return avg_velocity < 0.5 and variance < 0.1  # Low speed, consistent

    def _is_transport_pattern(self, velocities: List[float]) -> bool:
        """Detect transport pattern: smooth, continuous movement"""
        if len(velocities) < 5:
            return False

        # Transport has steady, moderate velocities
        avg_velocity = np.mean(velocities)
        variance = np.var(velocities)

        return 0.5 <= avg_velocity <= 2.0 and variance < 0.5  # Moderate, steady

    def _general_coordination(self, leader_action: Dict) -> Dict:
        """General coordination fallback"""
        actions = {}

        for key, value in leader_action.items():
            if key.startswith('left_'):
                # Mirror to both arms
                actions[key] = value
                right_key = key.replace('left_', 'right_')
                actions[right_key] = value

        return actions