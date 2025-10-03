"""
Enhanced BiManual Coordination Module

This module provides advanced algorithms for genuine bimanual coordination,
task-aware coordination, collision avoidance, spatial relationships, and
context-dependent strategies for 1-leader-to-2-followers control.

Phase 1: Basic coordination structure with collision detection and task detection foundations.
"""

from .enhanced_coordinator import EnhancedCoordinator, CoordinationMode
from .spatial_coordinator import SpatialCoordinator
from .task_aware_coordinator import TaskAwareCoordinator
from .safety_monitor import CoordinationSafetyMonitor, CollisionDetector

__all__ = [
    'EnhancedCoordinator',
    'SpatialCoordinator',
    'TaskAwareCoordinator',
    'CoordinationSafetyMonitor',
    'CollisionDetector',
    'CoordinationMode'
]