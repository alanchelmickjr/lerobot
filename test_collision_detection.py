#!/usr/bin/env python3
"""
Test script for SO-101 collision detection system.

This script demonstrates:
1. Collision detection when hand blocks movement
2. Intelligent backoff and retry
3. Auto-recalibration triggers
4. Adaptive performance monitoring
"""

import time
import sys
from typing import Dict, Any

# Try to import LeRobot
try:
    from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
except ImportError:
    print("❌ LeRobot not found. Please run: conda activate lerobot")
    sys.exit(1)


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Print test header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              🤖 SO-101 Collision Detection Test Suite 🤖             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")


def test_collision_with_hand_blocking(robot: SO101Follower):
    """Test collision detection by blocking with hand"""
    print(f"\n{Colors.YELLOW}Test 1: Hand Blocking Detection{Colors.RESET}")
    print("="*60)
    print("Instructions:")
    print("1. The arm will attempt to move to a new position")
    print("2. Place your hand gently in the path after movement starts")
    print("3. Hold firmly but safely - the arm should detect and back off")
    print("4. Remove your hand - the arm should retry")
    print(f"\n{Colors.RED}⚠️  Safety: Apply gentle, steady pressure only{Colors.RESET}")
    
    input(f"\n{Colors.GREEN}Press ENTER to start test...{Colors.RESET}")
    
    # Start movement
    print(f"\n{Colors.CYAN}Starting movement...{Colors.RESET}")
    start_pos = robot.bus.sync_read("Present_Position")
    print(f"Current positions: {start_pos}")
    
    # Move to a new position (adjust based on your setup)
    target_action = {
        "shoulder_pan.pos": 0.3,  # Adjust these values
        "elbow_flex.pos": 0.2,
    }
    
    print(f"Target positions: {target_action}")
    print(f"\n{Colors.YELLOW}NOW: Place your hand in the path!{Colors.RESET}")
    
    # Send action (collision detection happens automatically)
    result = robot.send_action(target_action)
    
    # Wait and check status
    time.sleep(5)
    
    # Get collision report
    status = robot.get_safety_status()
    if 'collision_detection' in status:
        collision_info = status['collision_detection']
        print(f"\n{Colors.CYAN}Collision Detection Report:{Colors.RESET}")
        print(f"  Total collisions: {collision_info['total_collisions']}")
        print(f"  Smoothness score: {collision_info['smoothness']:.2f}")
        print(f"  Monitoring frequency: {collision_info['monitoring_freq']:.1f}Hz")
        print(f"  Latency: {collision_info['latency_ms']:.1f}ms")
        
        if collision_info['total_collisions'] > 0:
            print(f"\n{Colors.GREEN}✅ Test PASSED: Collision detected!{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  No collision detected - try blocking more firmly{Colors.RESET}")
    
    return status


def test_wall_collision(robot: SO101Follower):
    """Test collision with solid obstacle"""
    print(f"\n{Colors.YELLOW}Test 2: Wall/Obstacle Collision{Colors.RESET}")
    print("="*60)
    print("Instructions:")
    print("1. Place a solid object (book, box) in the arm's path")
    print("2. The arm will attempt to move through it")
    print("3. Should detect, back off, and retry 3 times")
    print("4. After 3 retries, should abort movement")
    
    input(f"\n{Colors.GREEN}Place obstacle and press ENTER...{Colors.RESET}")
    
    # Attempt movement toward obstacle
    print(f"\n{Colors.CYAN}Attempting movement...{Colors.RESET}")
    
    target_action = {
        "shoulder_pan.pos": 0.5,  # Adjust based on obstacle position
        "elbow_flex.pos": 0.4,
    }
    
    start_time = time.time()
    result = robot.send_action(target_action)
    elapsed = time.time() - start_time
    
    print(f"\nMovement completed in {elapsed:.1f} seconds")
    
    # Check collision metrics
    status = robot.get_safety_status()
    if 'collision_detection' in status:
        collision_info = status['collision_detection']
        
        if collision_info['total_collisions'] >= 3:
            print(f"\n{Colors.GREEN}✅ Test PASSED: Multiple retries detected{Colors.RESET}")
            print(f"  Collisions: {collision_info['total_collisions']}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Expected 3+ collisions, got {collision_info['total_collisions']}{Colors.RESET}")
    
    return status


def test_adaptive_performance(robot: SO101Follower):
    """Test adaptive performance monitoring"""
    print(f"\n{Colors.YELLOW}Test 3: Adaptive Performance Monitoring{Colors.RESET}")
    print("="*60)
    print("Testing how system adapts monitoring frequency...")
    
    print(f"\n{Colors.CYAN}Performing rapid movements...{Colors.RESET}")
    
    frequencies = []
    smoothness_scores = []
    
    # Perform multiple movements
    for i in range(5):
        target = 0.1 + (i * 0.1)  # Gradually increase position
        action = {"shoulder_pan.pos": target}
        
        robot.send_action(action)
        time.sleep(1)
        
        # Get metrics
        status = robot.get_safety_status()
        if 'collision_detection' in status:
            info = status['collision_detection']
            frequencies.append(info['monitoring_freq'])
            smoothness_scores.append(info['smoothness'])
            
            print(f"  Move {i+1}: Freq={info['monitoring_freq']:.1f}Hz, "
                  f"Smoothness={info['smoothness']:.2f}, "
                  f"Latency={info['latency_ms']:.1f}ms")
    
    # Analyze adaptation
    if len(frequencies) > 1:
        freq_change = frequencies[-1] - frequencies[0]
        smooth_change = smoothness_scores[-1] - smoothness_scores[0]
        
        print(f"\n{Colors.CYAN}Performance Analysis:{Colors.RESET}")
        print(f"  Frequency adapted: {frequencies[0]:.1f}Hz → {frequencies[-1]:.1f}Hz")
        print(f"  Smoothness changed: {smoothness_scores[0]:.2f} → {smoothness_scores[-1]:.2f}")
        
        if abs(freq_change) > 0.5:
            print(f"\n{Colors.GREEN}✅ Test PASSED: System adapted frequency{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Minimal frequency adaptation observed{Colors.RESET}")
    
    return frequencies, smoothness_scores


def test_auto_recalibration_trigger(robot: SO101Follower):
    """Test auto-recalibration triggers"""
    print(f"\n{Colors.YELLOW}Test 4: Auto-Recalibration Triggers{Colors.RESET}")
    print("="*60)
    print("Testing recalibration triggers...")
    print("Note: This test simulates multiple collisions")
    
    if not robot.collision_system:
        print(f"{Colors.RED}Collision system not available{Colors.RESET}")
        return
    
    # Get initial collision count
    initial_collisions = robot.collision_system.collision_detector.total_collisions
    print(f"Initial collision count: {initial_collisions}")
    
    # Simulate multiple collisions (adjust threshold in config if needed)
    print(f"\n{Colors.CYAN}Simulating collision scenario...{Colors.RESET}")
    print("Place an obstacle that the arm will repeatedly hit")
    
    input(f"\n{Colors.GREEN}Press ENTER when obstacle is in place...{Colors.RESET}")
    
    # Attempt movements that will collide
    for i in range(6):  # Try to trigger recalibration (default is 5 collisions)
        print(f"\nAttempt {i+1}...")
        action = {"shoulder_pan.pos": 0.5}  # Adjust to hit obstacle
        robot.send_action(action)
        time.sleep(2)  # Wait for cooldown
    
    # Check if recalibration was triggered
    final_collisions = robot.collision_system.collision_detector.total_collisions
    collisions_detected = final_collisions - initial_collisions
    
    print(f"\n{Colors.CYAN}Results:{Colors.RESET}")
    print(f"  Collisions in test: {collisions_detected}")
    print(f"  Total collisions: {final_collisions}")
    
    if collisions_detected >= 5:
        print(f"\n{Colors.GREEN}✅ Recalibration should have been triggered{Colors.RESET}")
        print("  (Check for recalibration prompt above)")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Not enough collisions for auto-recalibration{Colors.RESET}")


def main():
    """Main test runner"""
    print_header()
    
    # Get port from user
    print(f"{Colors.CYAN}Enter the follower arm port:{Colors.RESET}")
    port = input("Port (e.g., /dev/cu.usbmodem...): ").strip()
    
    if not port:
        print(f"{Colors.RED}No port specified{Colors.RESET}")
        return
    
    # Configure robot with collision detection
    print(f"\n{Colors.CYAN}Configuring robot...{Colors.RESET}")
    config = SO101FollowerConfig(
        port=port,
        enable_collision_detection=True,
        enable_safety_monitoring=True,
        collision_current_threshold=800.0,  # Adjust sensitivity
        collision_duration=0.3,
        collision_max_retries=3,
        monitor_frequency=2.0
    )
    
    # Connect robot
    print(f"{Colors.CYAN}Connecting to robot...{Colors.RESET}")
    robot = SO101Follower(config)
    
    try:
        robot.connect(calibrate=False)
        print(f"{Colors.GREEN}✅ Robot connected{Colors.RESET}")
        
        # Run tests
        print(f"\n{Colors.BOLD}Available Tests:{Colors.RESET}")
        print("1. Hand Blocking Detection")
        print("2. Wall/Obstacle Collision")
        print("3. Adaptive Performance Monitoring")
        print("4. Auto-Recalibration Triggers")
        print("5. Run All Tests")
        print("6. Exit")
        
        while True:
            choice = input(f"\n{Colors.YELLOW}Select test (1-6): {Colors.RESET}").strip()
            
            if choice == "1":
                test_collision_with_hand_blocking(robot)
            elif choice == "2":
                test_wall_collision(robot)
            elif choice == "3":
                test_adaptive_performance(robot)
            elif choice == "4":
                test_auto_recalibration_trigger(robot)
            elif choice == "5":
                # Run all tests
                test_collision_with_hand_blocking(robot)
                test_wall_collision(robot)
                test_adaptive_performance(robot)
                test_auto_recalibration_trigger(robot)
                print(f"\n{Colors.GREEN}All tests completed!{Colors.RESET}")
            elif choice == "6":
                break
            else:
                print(f"{Colors.RED}Invalid choice{Colors.RESET}")
        
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
    
    finally:
        # Disconnect robot
        print(f"\n{Colors.CYAN}Disconnecting robot...{Colors.RESET}")
        robot.disconnect()
        print(f"{Colors.GREEN}✅ Test suite completed{Colors.RESET}")


if __name__ == "__main__":
    main()