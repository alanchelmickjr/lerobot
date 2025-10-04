#!/usr/bin/env python3

"""
Example script for autonomous LeRover operation.

This script demonstrates how to use LeRover with AI inference for autonomous navigation
and manipulation tasks.

Requirements:
- LeRover robot hardware
- Raspberry Pi with AI inference server (see ai_inference_server.py)
- SmolVLM model (optional, for local vision-language processing)
- ALOHA policy (optional, for advanced manipulation)

Usage:
1. Start the AI inference server on Raspberry Pi:
   python ai_inference_server.py

2. Run this script:
   python autonomous_lerover.py --task "Navigate to the red object and pick it up"
"""

import argparse
import logging
import time

from lerobot.robots.lerover import LeRover, LeRoverConfig, LeRoverAutonomyConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_lerover_config(args) -> LeRoverConfig:
    """Create LeRover configuration from command line arguments"""
    autonomy_config = LeRoverAutonomyConfig(
        enable_ai_inference=True,
        raspi_ip=args.raspi_ip,
        raspi_port=args.raspi_port,
        smolvlm_model_path=args.smolvlm_path,
        smolvlm_device=args.device,
        use_aloha_policy=args.use_aloha,
        aloha_model_path=args.aloha_path,
        autonomy_enabled=True,
        vision_fps=args.vision_fps,
        confidence_threshold=args.confidence,
        navigation_speed_mps=args.speed,
        max_autonomous_time_s=args.max_time,
    )

    config = LeRoverConfig(
        port=args.port,
        autonomy=autonomy_config,
    )

    return config


def main():
    parser = argparse.ArgumentParser(description="LeRover Autonomous Operation")
    parser.add_argument("--task", type=str, default="Navigate autonomously and avoid obstacles",
                       help="Task description for autonomous operation")
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                       help="Serial port for LeRover motors")
    parser.add_argument("--raspi-ip", type=str, default="192.168.1.100",
                       help="Raspberry Pi IP address")
    parser.add_argument("--raspi-port", type=int, default=8888,
                       help="AI inference server port")
    parser.add_argument("--smolvlm-path", type=str, default="",
                       help="Path to SmolVLM model (leave empty to disable)")
    parser.add_argument("--device", type=str, default="cpu",
                       choices=["cpu", "cuda"], help="Device for SmolVLM")
    parser.add_argument("--use-aloha", action="store_true",
                       help="Enable ALOHA policy for manipulation")
    parser.add_argument("--aloha-path", type=str, default="",
                       help="Path to ALOHA policy model")
    parser.add_argument("--vision-fps", type=int, default=10,
                       help="Vision processing frame rate")
    parser.add_argument("--confidence", type=float, default=0.7,
                       help="Minimum confidence threshold")
    parser.add_argument("--speed", type=float, default=0.2,
                       help="Navigation speed (m/s)")
    parser.add_argument("--max-time", type=int, default=300,
                       help="Maximum autonomous operation time (seconds)")

    args = parser.parse_args()

    try:
        # Create and configure LeRover
        logger.info("Initializing LeRover...")
        config = create_lerover_config(args)
        lerover = LeRover(config)

        # Connect to the robot
        logger.info("Connecting to LeRover...")
        lerover.connect()

        # Start autonomous operation
        logger.info(f"Starting autonomous operation with task: {args.task}")
        lerover.start_autonomy(args.task)

        # Monitor operation
        start_time = time.time()
        while lerover.autonomy_active and not lerover.emergency_stop:
            elapsed = time.time() - start_time
            logger.info(".1f")
            time.sleep(5.0)  # Log every 5 seconds

        logger.info("Autonomous operation completed")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error during autonomous operation: {e}")
    finally:
        if 'lerover' in locals():
            logger.info("Stopping LeRover...")
            lerover.stop_autonomy()
            lerover.disconnect()


if __name__ == "__main__":
    main()