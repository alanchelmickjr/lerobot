"""
Enhanced Coordinator

Advanced coordination algorithms for 1-leader-to-2-followers control.
Provides backward compatibility with existing coordinated mode while adding
advanced algorithms for genuine bimanual coordination.
"""

import numpy as np
import logging
from typing import Dict, Optional
from enum import Enum

from .spatial_coordinator import SpatialCoordinator
from .task_aware_coordinator import TaskAwareCoordinator, TaskType
from .safety_monitor import CoordinationSafetyMonitor

logger = logging.getLogger(__name__)


class CoordinationMode(Enum):
    """Coordination mode enumeration"""
    BASIC_COORDINATED = "basic_coordinated"  # Backward compatible simple mirroring
    ENHANCED_COORDINATED = "enhanced_coordinated"  # Advanced algorithms
    TASK_AWARE = "task_aware"  # Context-sensitive coordination
    SPATIAL_RELATIVE = "spatial_relative"  # Maintain spatial relationships
    SYNCHRONIZED = "synchronized"  # Time-synchronized movements


class EnhancedCoordinator:
    """Advanced coordination algorithms for 1-leader-to-2-followers control"""

    def __init__(self, coordination_mode: CoordinationMode = CoordinationMode.ENHANCED_COORDINATED):
        """
        Initialize enhanced coordinator

        Args:
            coordination_mode: Type of coordination to use
        """
        self.coordination_mode = coordination_mode
        self.task_context = TaskType.GENERAL

        # Initialize coordination components
        self.spatial_coordinator = SpatialCoordinator()
        self.task_coordinator = TaskAwareCoordinator()
        self.safety_monitor = CoordinationSafetyMonitor()

        # Statistics tracking
        self.stats = {
            'total_actions': 0,
            'safety_violations': 0,
            'task_switches': 0
        }

    def compute_coordinated_actions(self, leader_action: Dict,
                                   task_context: Optional[str] = None) -> Dict:
        """
        Compute sophisticated coordinated actions for both followers

        Args:
            leader_action: Single leader arm action
            task_context: Task type ("pick_place", "assembly", "transport", etc.)

        Returns:
            Dictionary with left and right follower actions
        """
        self.stats['total_actions'] += 1

        # Update task context if provided
        if task_context:
            try:
                self.task_context = TaskType(task_context)
            except ValueError:
                self.task_context = TaskType.GENERAL

        # Update trajectory for task detection
        self.task_coordinator.update_trajectory_context(leader_action)

        # Auto-detect task if in task-aware mode
        if self.coordination_mode == CoordinationMode.TASK_AWARE:
            detected_task = self.task_coordinator.detect_task_context(
                self.task_coordinator.trajectory_buffer[-20:] if len(self.task_coordinator.trajectory_buffer) > 20
                else self.task_coordinator.trajectory_buffer
            )
            if detected_task != self.task_context:
                self.task_context = detected_task
                self.stats['task_switches'] += 1
                logger.info(f"Task context switched to: {detected_task.value}")

        # Compute coordinated actions based on mode
        if self.coordination_mode == CoordinationMode.BASIC_COORDINATED:
            coordinated_actions = self._basic_coordination(leader_action)
        elif self.coordination_mode == CoordinationMode.ENHANCED_COORDINATED:
            coordinated_actions = self._enhanced_coordination(leader_action)
        elif self.coordination_mode == CoordinationMode.TASK_AWARE:
            coordinated_actions = self.task_coordinator.adapt_coordination(
                self.task_context, leader_action
            )
        elif self.coordination_mode == CoordinationMode.SPATIAL_RELATIVE:
            coordinated_actions = self.spatial_coordinator.optimize_workspace_usage(leader_action)
        elif self.coordination_mode == CoordinationMode.SYNCHRONIZED:
            coordinated_actions = self._synchronized_coordination(leader_action)
        else:
            coordinated_actions = self._basic_coordination(leader_action)

        # Apply safety validation
        is_safe, warnings = self.safety_monitor.validate_coordinated_action(
            self._extract_left_actions(coordinated_actions),
            self._extract_right_actions(coordinated_actions)
        )

        if not is_safe:
            self.stats['safety_violations'] += 1
            logger.warning(f"Safety violation detected: {warnings}")
            if self.safety_monitor.is_emergency_stop_active():
                # Return safe stop actions
                return self._emergency_stop_actions()
            else:
                # Try to adjust for safety
                coordinated_actions = self._adjust_for_safety(coordinated_actions, warnings)

        return coordinated_actions

    def set_coordination_mode(self, mode: CoordinationMode) -> None:
        """Set the coordination mode"""
        self.coordination_mode = mode
        logger.info(f"Coordination mode set to: {mode.value}")

    def get_coordination_stats(self) -> Dict:
        """Get coordination statistics"""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset coordination statistics"""
        self.stats = {
            'total_actions': 0,
            'safety_violations': 0,
            'task_switches': 0
        }

    def _basic_coordination(self, leader_action: Dict) -> Dict:
        """Basic coordination (backward compatible with existing simple_touch_ui.py)"""
        coordinated_action = {}

        for key, value in leader_action.items():
            if key.startswith('left_'):
                # Send to left follower
                coordinated_action[key] = value
                # Mirror to right follower
                right_key = key.replace('left_', 'right_')
                coordinated_action[right_key] = value

        return coordinated_action

    def _enhanced_coordination(self, leader_action: Dict) -> Dict:
        """Enhanced coordination with task awareness and spatial reasoning"""
        # Use task-aware coordination with current context
        return self.task_coordinator.adapt_coordination(self.task_context, leader_action)

    def _synchronized_coordination(self, leader_action: Dict) -> Dict:
        """Time-synchronized movements with phase coordination"""
        # Basic synchronized implementation (placeholder for advanced timing)
        return self._basic_coordination(leader_action)

    def _extract_left_actions(self, coordinated_actions: Dict) -> Dict:
        """Extract left arm actions from coordinated actions"""
        return {k: v for k, v in coordinated_actions.items() if k.startswith('left_')}

    def _extract_right_actions(self, coordinated_actions: Dict) -> Dict:
        """Extract right arm actions from coordinated actions"""
        return {k: v for k, v in coordinated_actions.items() if k.startswith('right_')}

    def _emergency_stop_actions(self) -> Dict:
        """Generate emergency stop actions"""
        # Return zero actions for all joints
        stop_actions = {}
        joint_keys = ['left_arm_joint_1', 'left_arm_joint_2', 'left_arm_joint_3',
                     'left_arm_joint_4', 'left_arm_joint_5', 'left_arm_joint_6',
                     'right_arm_joint_1', 'right_arm_joint_2', 'right_arm_joint_3',
                     'right_arm_joint_4', 'right_arm_joint_5', 'right_arm_joint_6']

        for key in joint_keys:
            stop_actions[key] = 0.0

        return stop_actions

    def _adjust_for_safety(self, coordinated_actions: Dict, warnings: list) -> Dict:
        """Adjust actions to address safety warnings"""
        adjusted_actions = coordinated_actions.copy()

        # Basic safety adjustments (placeholder for advanced collision avoidance)
        for warning in warnings:
            if "collision" in warning.lower():
                # Reduce movement magnitude to avoid collision
                for key, value in adjusted_actions.items():
                    if isinstance(value, (int, float)):
                        adjusted_actions[key] = value * 0.5  # Reduce by half

        return adjusted_actions