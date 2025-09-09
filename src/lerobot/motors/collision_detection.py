"""
Collision Detection and Intelligent Backoff System for SO-101 Robot Arms

This module provides advanced collision detection with intelligent backoff,
auto-recalibration triggers, and adaptive performance monitoring.
"""

import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from threading import Lock, Event

logger = logging.getLogger(__name__)


@dataclass
class CollisionConfig:
    """Configuration for collision detection"""
    # Collision detection thresholds
    torque_threshold: float = 0.3  # Normalized torque threshold (0-1)
    current_threshold: float = 900.0  # mA
    collision_duration: float = 0.3  # seconds of sustained force
    
    # Backoff parameters
    backoff_distance: float = 0.1  # Normalized position units
    backoff_speed: float = 0.5  # Speed multiplier for backoff
    cooldown_period: float = 2.0  # seconds before retry allowed
    max_retries: int = 3  # Maximum collision retries before abort
    
    # Auto-recalibration triggers
    position_error_threshold: float = 0.05  # Position error triggering recalibration
    consecutive_collisions_for_recal: int = 5  # Collisions before recalibration
    time_since_last_calibration: float = 3600.0  # seconds (1 hour)


@dataclass
class PerformanceMetrics:
    """Metrics for adaptive performance monitoring"""
    smoothness_score: float = 1.0  # 0-1 score, 1 is perfectly smooth
    latency_ms: float = 0.0  # Average loop latency
    cpu_usage: float = 0.0  # CPU usage percentage
    monitoring_frequency: float = 2.0  # Current monitoring Hz
    optimal_frequency: float = 2.0  # Calculated optimal Hz
    
    # Historical tracking
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))
    smoothness_history: deque = field(default_factory=lambda: deque(maxlen=100))
    position_jitter: deque = field(default_factory=lambda: deque(maxlen=50))


class CollisionDetector:
    """
    Advanced collision detection system with intelligent backoff
    and auto-recalibration capabilities.
    """
    
    def __init__(
        self,
        motors_bus,
        config: Optional[CollisionConfig] = None,
        recalibration_callback: Optional[Callable] = None
    ):
        """
        Initialize collision detector
        
        Args:
            motors_bus: The motor bus for reading sensor data
            config: Collision detection configuration
            recalibration_callback: Function to call for recalibration
        """
        self.bus = motors_bus
        self.config = config or CollisionConfig()
        self.recalibration_callback = recalibration_callback
        
        # Collision tracking per motor
        self.collision_state: Dict[str, Dict] = {}
        self.collision_history: Dict[str, List] = {}
        self.backoff_positions: Dict[str, float] = {}
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.last_positions: Dict[str, float] = {}
        self.last_velocities: Dict[str, float] = {}
        
        # Calibration tracking
        self.last_calibration_time = time.time()
        self.total_collisions = 0
        
        # Thread safety
        self.lock = Lock()
        self.active = False
        
        # Initialize motor states
        self._initialize_motor_states()
    
    def _initialize_motor_states(self):
        """Initialize tracking for each motor"""
        for motor_name in self.bus.motors:
            self.collision_state[motor_name] = {
                'detecting': False,
                'collision_start': None,
                'backed_off': False,
                'retry_count': 0,
                'last_collision': None,
                'cooldown_until': 0
            }
            self.collision_history[motor_name] = deque(maxlen=10)
    
    def detect_collision(
        self,
        motor: str,
        current: float,
        position: float,
        target_position: float,
        load: Optional[float] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Detect collision for a specific motor
        
        Args:
            motor: Motor name
            current: Current draw in mA
            position: Current position (normalized)
            target_position: Target position (normalized)
            load: Optional load/torque reading
        
        Returns:
            Tuple of (collision_detected, action_dict)
        """
        with self.lock:
            state = self.collision_state[motor]
            current_time = time.time()
            
            # Check if in cooldown period
            if current_time < state['cooldown_until']:
                return False, {'action': 'cooldown', 'time_remaining': state['cooldown_until'] - current_time}
            
            # Calculate position error
            position_error = abs(target_position - position)
            
            # Determine if experiencing resistance
            is_resisting = (
                current > self.config.current_threshold or
                (load is not None and abs(load) > self.config.torque_threshold)
            ) and position_error > 0.02  # Not at target
            
            if is_resisting:
                # Start or continue collision detection
                if not state['detecting']:
                    state['detecting'] = True
                    state['collision_start'] = current_time
                    logger.debug(f"Motor {motor}: Collision detection started (current={current:.1f}mA)")
                
                # Check if collision duration exceeded
                collision_duration = current_time - state['collision_start']
                
                if collision_duration >= self.config.collision_duration:
                    # Collision confirmed!
                    state['detecting'] = False
                    state['last_collision'] = current_time
                    state['retry_count'] += 1
                    self.total_collisions += 1
                    
                    # Record collision
                    self.collision_history[motor].append({
                        'time': current_time,
                        'position': position,
                        'target': target_position,
                        'current': current,
                        'load': load
                    })
                    
                    # Determine backoff action
                    if state['retry_count'] >= self.config.max_retries:
                        # Too many retries, abort movement
                        logger.warning(f"Motor {motor}: Max retries exceeded, aborting movement")
                        return True, {
                            'action': 'abort',
                            'reason': 'max_retries_exceeded',
                            'should_recalibrate': self._should_recalibrate()
                        }
                    
                    # Calculate backoff position
                    backoff_direction = np.sign(position - target_position)
                    backoff_position = position + (backoff_direction * self.config.backoff_distance)
                    
                    # Ensure backoff stays within limits
                    if motor in self.bus.motors:
                        motor_obj = self.bus.motors[motor]
                        if hasattr(motor_obj, 'range_min') and hasattr(motor_obj, 'range_max'):
                            backoff_position = np.clip(
                                backoff_position,
                                motor_obj.range_min,
                                motor_obj.range_max
                            )
                    
                    self.backoff_positions[motor] = backoff_position
                    state['backed_off'] = True
                    state['cooldown_until'] = current_time + self.config.cooldown_period
                    
                    logger.info(f"Motor {motor}: Collision detected! Backing off to {backoff_position:.3f}")
                    
                    return True, {
                        'action': 'backoff',
                        'backoff_position': backoff_position,
                        'retry_count': state['retry_count'],
                        'cooldown_period': self.config.cooldown_period,
                        'should_recalibrate': self._should_recalibrate()
                    }
            else:
                # No resistance detected
                if state['detecting']:
                    state['detecting'] = False
                    state['collision_start'] = None
                
                # Reset retry count if successfully moved after backoff
                if state['backed_off'] and position_error < 0.05:
                    state['backed_off'] = False
                    state['retry_count'] = 0
                    logger.debug(f"Motor {motor}: Successfully moved after backoff")
            
            return False, None
    
    def _should_recalibrate(self) -> bool:
        """
        Determine if auto-recalibration should be triggered
        
        Returns:
            True if recalibration is recommended
        """
        current_time = time.time()
        
        # Check time since last calibration
        if (current_time - self.last_calibration_time) > self.config.time_since_last_calibration:
            logger.info("Recalibration recommended: Time threshold exceeded")
            return True
        
        # Check total collision count
        if self.total_collisions >= self.config.consecutive_collisions_for_recal:
            logger.info(f"Recalibration recommended: {self.total_collisions} collisions detected")
            return True
        
        # Check for persistent position errors
        for motor, history in self.collision_history.items():
            if len(history) >= 3:
                recent_collisions = list(history)[-3:]
                # If last 3 collisions were at similar positions, might be calibration issue
                positions = [c['position'] for c in recent_collisions]
                if np.std(positions) < 0.02:  # Low variance in collision positions
                    logger.info(f"Recalibration recommended: Repeated collisions at same position for {motor}")
                    return True
        
        return False
    
    def trigger_recalibration(self):
        """Trigger auto-recalibration if callback is set"""
        if self.recalibration_callback:
            logger.info("Triggering auto-recalibration...")
            self.last_calibration_time = time.time()
            self.total_collisions = 0
            
            # Clear collision history
            for motor in self.collision_history:
                self.collision_history[motor].clear()
            
            # Execute recalibration
            try:
                self.recalibration_callback()
            except Exception as e:
                logger.error(f"Recalibration failed: {e}")
    
    def update_smoothness_metrics(
        self,
        positions: Dict[str, float],
        timestamp: float
    ) -> float:
        """
        Update smoothness metrics and calculate optimal monitoring frequency
        
        Args:
            positions: Current motor positions
            timestamp: Current timestamp
        
        Returns:
            Smoothness score (0-1, higher is smoother)
        """
        with self.lock:
            # Calculate position changes (jitter)
            if self.last_positions:
                position_deltas = []
                for motor, pos in positions.items():
                    if motor in self.last_positions:
                        delta = abs(pos - self.last_positions[motor])
                        position_deltas.append(delta)
                        self.metrics.position_jitter.append(delta)
                
                # Calculate smoothness based on jitter
                if position_deltas:
                    avg_jitter = np.mean(position_deltas)
                    # Smoothness inversely proportional to jitter
                    smoothness = max(0, 1.0 - (avg_jitter * 10))  # Scale factor
                    self.metrics.smoothness_score = smoothness
                    self.metrics.smoothness_history.append(smoothness)
            
            self.last_positions = positions.copy()
            
            # Adaptive frequency calculation
            self._calculate_optimal_frequency()
            
            return self.metrics.smoothness_score
    
    def _calculate_optimal_frequency(self):
        """
        Calculate optimal monitoring frequency based on performance metrics
        """
        if len(self.metrics.smoothness_history) < 10:
            return  # Not enough data
        
        recent_smoothness = np.mean(list(self.metrics.smoothness_history)[-10:])
        recent_latency = np.mean(list(self.metrics.latency_history)[-10:]) if self.metrics.latency_history else 0
        
        # Adjust frequency based on smoothness and latency
        if recent_smoothness < 0.7 and recent_latency < 20:
            # Poor smoothness but low latency - increase frequency
            self.metrics.optimal_frequency = min(10.0, self.metrics.monitoring_frequency * 1.5)
        elif recent_smoothness > 0.9 and recent_latency > 50:
            # Good smoothness but high latency - decrease frequency
            self.metrics.optimal_frequency = max(1.0, self.metrics.monitoring_frequency * 0.7)
        elif recent_latency > 100:
            # Very high latency - significantly decrease frequency
            self.metrics.optimal_frequency = max(0.5, self.metrics.monitoring_frequency * 0.5)
        else:
            # Gradually converge to optimal
            target = 2.0  # Default target
            if recent_smoothness > 0.8:
                target = 2.0
            elif recent_smoothness > 0.6:
                target = 5.0
            else:
                target = 8.0
            
            self.metrics.optimal_frequency = (
                0.7 * self.metrics.monitoring_frequency + 0.3 * target
            )
        
        logger.debug(
            f"Performance: smoothness={recent_smoothness:.2f}, "
            f"latency={recent_latency:.1f}ms, "
            f"optimal_freq={self.metrics.optimal_frequency:.1f}Hz"
        )
    
    def get_adaptive_frequency(self) -> float:
        """
        Get the current adaptive monitoring frequency
        
        Returns:
            Optimal frequency in Hz
        """
        return self.metrics.optimal_frequency
    
    def record_latency(self, latency_ms: float):
        """Record processing latency for adaptive monitoring"""
        self.metrics.latency_history.append(latency_ms)
        self.metrics.latency_ms = np.mean(list(self.metrics.latency_history)[-10:])


class SmartCollisionSafetySystem:
    """
    Integrated collision detection and safety system for SO-101
    """
    
    def __init__(
        self,
        robot,
        collision_config: Optional[CollisionConfig] = None
    ):
        """
        Initialize smart collision safety system
        
        Args:
            robot: The SO101 robot instance
            collision_config: Collision detection configuration
        """
        self.robot = robot
        self.bus = robot.bus
        
        # Initialize collision detector with recalibration callback
        self.collision_detector = CollisionDetector(
            self.bus,
            collision_config,
            recalibration_callback=self._trigger_recalibration
        )
        
        # Track active movements
        self.active_movements: Dict[str, Dict] = {}
        self.movement_lock = Lock()
        
        logger.info("Smart Collision Safety System initialized")
    
    def safe_move_with_collision_detection(
        self,
        goal_positions: Dict[str, float],
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Execute movement with collision detection and intelligent backoff
        
        Args:
            goal_positions: Target positions for motors
            timeout: Maximum time for movement
        
        Returns:
            Result dictionary with status and any collision events
        """
        start_time = time.time()
        result = {
            'success': False,
            'collisions': {},
            'final_positions': {},
            'recalibration_triggered': False
        }
        
        with self.movement_lock:
            # Store active movements
            for motor, target in goal_positions.items():
                self.active_movements[motor] = {
                    'target': target,
                    'backed_off': False,
                    'abort': False
                }
        
        try:
            while (time.time() - start_time) < timeout:
                loop_start = time.time()
                
                # Read current state
                positions = self.bus.sync_read("Present_Position")
                currents = self.bus.sync_read("Present_Current")
                loads = self.bus.sync_read("Present_Load")
                
                # Update smoothness metrics
                smoothness = self.collision_detector.update_smoothness_metrics(
                    positions, time.time()
                )
                
                # Check each motor for collisions
                movements_complete = True
                
                for motor, target in goal_positions.items():
                    if self.active_movements[motor]['abort']:
                        continue
                    
                    current_pos = positions.get(motor, 0)
                    current_current = currents.get(motor, 0)
                    current_load = loads.get(motor, 0) / 1000.0  # Normalize
                    
                    # Check for collision
                    collision_detected, action = self.collision_detector.detect_collision(
                        motor,
                        current_current,
                        current_pos,
                        target,
                        current_load
                    )
                    
                    if collision_detected:
                        result['collisions'][motor] = action
                        
                        if action['action'] == 'backoff':
                            # Execute backoff
                            backoff_pos = action['backoff_position']
                            self.bus.write("Goal_Position", motor, backoff_pos)
                            self.active_movements[motor]['backed_off'] = True
                            logger.info(f"Motor {motor}: Executing backoff to {backoff_pos:.3f}")
                            
                        elif action['action'] == 'abort':
                            # Abort this motor's movement
                            self.active_movements[motor]['abort'] = True
                            logger.warning(f"Motor {motor}: Movement aborted")
                        
                        # Check for recalibration
                        if action.get('should_recalibrate', False):
                            result['recalibration_triggered'] = True
                            self.collision_detector.trigger_recalibration()
                    
                    # Check if at target (or backed off)
                    if not self.active_movements[motor]['abort']:
                        target_pos = (
                            action['backoff_position']
                            if self.active_movements[motor]['backed_off']
                            else target
                        )
                        if abs(current_pos - target_pos) > 0.02:
                            movements_complete = False
                
                # Record latency for adaptive monitoring
                loop_latency = (time.time() - loop_start) * 1000
                self.collision_detector.record_latency(loop_latency)
                
                # Adjust sleep based on adaptive frequency
                optimal_freq = self.collision_detector.get_adaptive_frequency()
                sleep_time = max(0, (1.0 / optimal_freq) - (time.time() - loop_start))
                
                if movements_complete:
                    result['success'] = True
                    break
                
                time.sleep(sleep_time)
            
            # Record final positions
            result['final_positions'] = self.bus.sync_read("Present_Position")
            
            # Log performance metrics
            metrics = self.collision_detector.metrics
            logger.info(
                f"Movement complete. Smoothness: {metrics.smoothness_score:.2f}, "
                f"Latency: {metrics.latency_ms:.1f}ms, "
                f"Frequency: {metrics.optimal_frequency:.1f}Hz"
            )
            
        except Exception as e:
            logger.error(f"Error during safe movement: {e}")
            result['error'] = str(e)
        
        finally:
            self.active_movements.clear()
        
        return result
    
    def _trigger_recalibration(self):
        """Trigger robot recalibration"""
        try:
            logger.info("Auto-recalibration triggered by collision detection")
            
            # Disable torque for safety
            self.bus.disable_torque()
            
            # Notify user
            print("\n" + "="*60)
            print("⚠️  AUTO-RECALIBRATION REQUIRED")
            print("="*60)
            print("Multiple collisions detected. Recalibration recommended.")
            print("Please move the arm to the middle position and press ENTER...")
            input()
            
            # Run calibration
            self.robot.calibrate()
            
            # Re-enable torque
            self.bus.enable_torque()
            
            logger.info("Auto-recalibration completed successfully")
            
        except Exception as e:
            logger.error(f"Auto-recalibration failed: {e}")