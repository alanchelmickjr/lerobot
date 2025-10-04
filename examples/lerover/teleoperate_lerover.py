#!/usr/bin/env python3

"""
Example script for teleoperating LeRover with autonomy features.

This script allows manual control of LeRover while also providing autonomy controls.

Controls:
- WASD: Movement (forward/backward/left/right)
- Z/X: Rotate left/right
- R/F: Speed up/down
- T: Toggle autonomy mode
- E: Emergency stop
- Q: Quit

When autonomy is enabled, the robot will use AI for autonomous navigation.
"""

import logging
import time

from lerobot.robots.lerover import LeRoverClient, LeRoverClientConfig, LeRoverAutonomyConfig
from lerobot.teleoperators.keyboard import KeyboardTeleoperator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Configure LeRover client
    autonomy_config = LeRoverAutonomyConfig(
        enable_ai_inference=True,
        raspi_ip="192.168.1.100",  # Change to your Raspberry Pi IP
        raspi_port=8888,
        smolvlm_model_path="",  # Set path if available
        autonomy_enabled=False,  # Start in manual mode
    )

    robot_config = LeRoverClientConfig(
        remote_ip="192.168.1.100",  # Change to your robot's IP
        autonomy=autonomy_config,
    )

    # Create teleoperator
    teleop_config = KeyboardTeleoperator.default_config()
    teleop = KeyboardTeleoperator(teleop_config)

    # Create LeRover client
    robot = LeRoverClient(robot_config)

    try:
        # Connect to the robot
        logger.info("Connecting to LeRover...")
        robot.connect()
        teleop.connect()

        logger.info("Starting teleoperation...")
        logger.info("Controls: WASD (move), ZX (rotate), RF (speed), T (autonomy), E (emergency), Q (quit)")

        last_autonomy_status = False

        while True:
            # Get keyboard input
            pressed_keys = teleop.get_keys()

            # Check for quit
            if "q" in pressed_keys:
                logger.info("Quit command received")
                break

            # Handle autonomy toggle
            if "t" in pressed_keys:
                robot.toggle_autonomy()
                autonomy_status = "ENABLED" if robot.autonomy_enabled else "DISABLED"
                logger.info(f"Autonomy {autonomy_status}")

            # Handle emergency stop
            if "e" in pressed_keys:
                robot.emergency_stop()
                logger.warning("Emergency stop activated")

            # Get robot observation
            obs = robot.get_observation()

            # Log autonomy status changes
            current_autonomy = obs.get("autonomy_active", 0.0) > 0.5
            if current_autonomy != last_autonomy_status:
                status = "ACTIVE" if current_autonomy else "INACTIVE"
                logger.info(f"LeRover autonomy: {status}")
                last_autonomy_status = current_autonomy

            # Call teleoperator to get action
            action = teleop(obs)

            # Add autonomy status to action
            action["autonomy_active"] = float(robot.autonomy_enabled)
            action["emergency_stop"] = 0.0  # Will be set by emergency_stop() method

            # Send action to robot
            robot.send_action(action)

            # Small delay to prevent overwhelming the connection
            time.sleep(0.05)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error during teleoperation: {e}")
    finally:
        logger.info("Disconnecting...")
        robot.disconnect()
        teleop.disconnect()


if __name__ == "__main__":
    main()