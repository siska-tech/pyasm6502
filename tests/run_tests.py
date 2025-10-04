#!/usr/bin/env python3
"""
pyasm6502 - Test Runner
Main test runner that coordinates all test suites
"""

import sys
import subprocess
from pathlib import Path

def run_test_script(script_name: str, description: str) -> bool:
    """Run a test script and return success status."""
    print(f"\n[TEST] {description}")
    print(f"   Running: {script_name}")
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"   [FAIL] Script not found: {script_name}")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   [PASS] {description}")
            return True
        else:
            print(f"   [FAIL] {description}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def main():
    """Run all available test suites."""
    print("pyasm6502 - Test Runner")
    print("=" * 50)
    
    # Available test suites
    test_suites = [
        ("quick_test.py", "Basic functionality tests"),
        ("check_acme_compatibility.py", "ACME compatibility tests"),
    ]
    
    passed = 0
    total = len(test_suites)
    
    for script_name, description in test_suites:
        if run_test_script(script_name, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Overall Summary: {passed}/{total} test suites passed")
    
    if passed == total:
        print("[SUCCESS] All test suites passed!")
        return 0
    else:
        print("[WARNING] Some test suites failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
