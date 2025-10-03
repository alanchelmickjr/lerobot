#!/usr/bin/env python3
"""
Test script to verify the EOF error fixes and logging implementation
in lerobot_bimanual_ui.py
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    try:
        from lerobot_bimanual_ui import UILogger, logger, Colors
        print("✅ Imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_logger_creation():
    """Test UILogger class creation and methods"""
    print("\nTesting UILogger class...")
    try:
        from lerobot_bimanual_ui import UILogger
        
        # Create logger instance
        test_logger = UILogger("test_bimanual.log")
        
        # Test logging methods
        test_logger.info("Test info message")
        test_logger.warning("Test warning message")
        test_logger.error("Test error message")
        
        # Check that messages were stored
        logs = test_logger.get_recent_logs(10)
        assert len(logs) >= 3, "Not enough logs stored"
        assert any("INFO" in log for log in logs), "No INFO logs found"
        assert any("WARNING" in log for log in logs), "No WARNING logs found"
        assert any("ERROR" in log for log in logs), "No ERROR logs found"
        
        # Test clear
        test_logger.clear()
        assert len(test_logger.get_recent_logs()) == 0, "Clear didn't work"
        
        print("✅ UILogger class works correctly")
        
        # Clean up test log file
        if os.path.exists("test_bimanual.log"):
            os.remove("test_bimanual.log")
        
        return True
    except Exception as e:
        print(f"❌ UILogger test failed: {e}")
        return False

def test_global_logger():
    """Test that global logger instance exists"""
    print("\nTesting global logger instance...")
    try:
        from lerobot_bimanual_ui import logger
        
        # Test that logger methods exist
        assert hasattr(logger, 'info'), "Logger missing info method"
        assert hasattr(logger, 'error'), "Logger missing error method"
        assert hasattr(logger, 'warning'), "Logger missing warning method"
        assert hasattr(logger, 'get_recent_logs'), "Logger missing get_recent_logs method"
        
        print("✅ Global logger instance exists and has required methods")
        return True
    except Exception as e:
        print(f"❌ Global logger test failed: {e}")
        return False

def test_code_structure():
    """Test that the code has the required fixes"""
    print("\nTesting code structure for fixes...")
    
    try:
        # Read the file
        with open('lerobot_bimanual_ui.py', 'r') as f:
            content = f.read()
        
        # Check for calibrate=False in connect calls
        connect_calibrate_count = content.count('connect(calibrate=False)')
        assert connect_calibrate_count >= 3, f"Expected at least 3 'connect(calibrate=False)' calls, found {connect_calibrate_count}"
        
        # Check for UILogger class
        assert 'class UILogger:' in content, "UILogger class not found"
        
        # Check for error handling with EOFError
        assert 'except EOFError:' in content, "EOFError handling not found"
        
        # Check for logging imports
        assert 'import logging' in content, "logging import not found"
        assert 'from datetime import datetime' in content, "datetime import not found"
        
        # Check for logger usage
        assert 'logger.info(' in content, "logger.info() calls not found"
        assert 'logger.error(' in content, "logger.error() calls not found"
        
        # Check for log viewer menu option
        assert '📋 View System Logs' in content, "Log viewer menu option not found"
        
        print("✅ All required code fixes are present")
        return True
    except FileNotFoundError:
        print("❌ lerobot_bimanual_ui.py not found")
        return False
    except Exception as e:
        print(f"❌ Code structure test failed: {e}")
        return False

def test_error_messages():
    """Test that proper error messages are in place"""
    print("\nTesting error messages...")
    
    try:
        with open('lerobot_bimanual_ui.py', 'r') as f:
            content = f.read()
        
        # Check for calibration error messages
        assert 'must be calibrated before use' in content, "Calibration error message not found"
        
        # Check for connection error handling
        assert 'Connection failed' in content or 'connection failed' in content, "Connection error message not found"
        
        print("✅ Error messages are properly implemented")
        return True
    except Exception as e:
        print(f"❌ Error message test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("="*70)
    print("🧪 Testing Bimanual UI Fixes")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("UILogger Class", test_logger_creation),
        ("Global Logger", test_global_logger),
        ("Code Structure", test_code_structure),
        ("Error Messages", test_error_messages),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*70)
    print("📊 Test Results Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())