#!/usr/bin/env python3
"""
Verification Test Script for Coordinated Arm Control Fix

This script verifies that the port duplication bug fix is working correctly:
1. Configuration validation catches duplicate ports
2. Distinct ports are accepted properly
3. Mirror mode (None port) still works
4. simple_touch_ui.py has the correct fix applied
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_duplicate_ports_rejected():
    """Test 1: Configuration Validation - Duplicate ports should be rejected"""
    print("\n" + "="*60)
    print("TEST 1: Duplicate Port Validation")
    print("="*60)
    
    from src.lerobot.teleoperators.bi_so100_leader.config_bi_so100_leader import BiSO100LeaderConfig
    
    try:
        bad_config = BiSO100LeaderConfig(
            left_arm_port="/dev/ttyACM0",
            right_arm_port="/dev/ttyACM0",  # Duplicate - should raise error
            id="test"
        )
        print("❌ FAIL: Duplicate ports not caught by validation")
        return False
    except ValueError as e:
        print(f"✅ PASS: Duplicate ports correctly rejected: {e}")
        return True
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False


def test_distinct_ports_accepted():
    """Test 2: Correct Port Configuration - Distinct ports should be accepted"""
    print("\n" + "="*60)
    print("TEST 2: Distinct Port Configuration")
    print("="*60)
    
    from src.lerobot.teleoperators.bi_so100_leader.config_bi_so100_leader import BiSO100LeaderConfig
    
    try:
        good_config = BiSO100LeaderConfig(
            left_arm_port="/dev/ttyACM0",
            right_arm_port="/dev/ttyACM1",  # Distinct - should work
            id="test"
        )
        print("✅ PASS: Distinct ports accepted")
        return True
    except ValueError as e:
        print(f"❌ FAIL: Distinct ports rejected: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False


def test_mirror_mode_none_port():
    """Test 3: Mirror Mode - None port should be allowed"""
    print("\n" + "="*60)
    print("TEST 3: Mirror Mode (None Port)")
    print("="*60)
    
    from src.lerobot.teleoperators.bi_so100_leader.config_bi_so100_leader import BiSO100LeaderConfig
    
    try:
        mirror_config = BiSO100LeaderConfig(
            left_arm_port="/dev/ttyACM0",
            right_arm_port=None,  # None for mirror mode - should work
            id="mirror"
        )
        print("✅ PASS: Mirror mode (None port) accepted")
        return True
    except ValueError as e:
        print(f"❌ FAIL: Mirror mode rejected: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False


def test_simple_touch_ui_fix():
    """Test 4: Verify simple_touch_ui.py fix"""
    print("\n" + "="*60)
    print("TEST 4: Verify simple_touch_ui.py Fix")
    print("="*60)
    
    ui_file = Path("simple_touch_ui.py")
    
    if not ui_file.exists():
        print("⚠️  WARNING: simple_touch_ui.py not found - skipping this test")
        return None  # Not a failure, just not applicable
    
    try:
        with open(ui_file, "r") as f:
            content = f.read()
        
        results = []
        
        # Check for the fix around line 346
        if "right_arm_port=ports['right_leader']" in content:
            print("✅ PASS: simple_touch_ui.py uses distinct ports")
            results.append(True)
        else:
            print("❌ FAIL: simple_touch_ui.py missing correct port assignment")
            results.append(False)
        
        # Make sure we don't have the old bug
        if "right_arm_port=ports['left_leader']" in content:
            print("❌ FAIL: simple_touch_ui.py still has duplicate port bug")
            results.append(False)
        else:
            print("✅ PASS: simple_touch_ui.py duplicate port bug removed")
            results.append(True)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ FAIL: Error reading simple_touch_ui.py: {e}")
        return False


def print_summary(results):
    """Test 5: Print summary of all tests"""
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    test_names = [
        "Port validation working",
        "Distinct ports configuration working",
        "Mirror mode still supported",
        "simple_touch_ui.py bug fixed"
    ]
    
    all_passed = True
    for name, result in zip(test_names, results):
        if result is None:
            print(f"⚠️  {name} (skipped)")
        elif result:
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("\n🎉 SUCCESS: The coordinated arm control fix is verified!")
        print("All critical functionality is working as expected.")
        return 0
    else:
        print("\n⚠️  ISSUES FOUND: Some tests failed.")
        print("Please review the output above for details.")
        return 1


def main():
    """Run all verification tests"""
    print("="*60)
    print("COORDINATED ARM CONTROL FIX VERIFICATION")
    print("="*60)
    print("\nThis script verifies the port duplication bug fix:")
    print("- Configuration validates against duplicate ports")
    print("- Distinct ports work correctly")
    print("- Mirror mode is still supported")
    print("- simple_touch_ui.py has the fix applied")
    
    # Run all tests
    results = [
        test_duplicate_ports_rejected(),
        test_distinct_ports_accepted(),
        test_mirror_mode_none_port(),
        test_simple_touch_ui_fix()
    ]
    
    # Print summary and return exit code
    exit_code = print_summary(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()