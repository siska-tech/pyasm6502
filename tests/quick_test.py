#!/usr/bin/env python3
"""
pyasm6502 - Quick Test Runner
Simple test runner for basic functionality validation
"""

import sys
import subprocess
from pathlib import Path

def run_assembler_test(source_code: str, description: str, should_fail: bool = False) -> bool:
    """Run a simple assembler test with inline source code."""
    print(f"\n[TEST] {description}")
    
    # Create temporary source file
    temp_file = Path("temp_test.a")
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(source_code)
        
        # Run assembler using the installed command
        cmd = [
            "pyasm6502",
            str(temp_file),
            "-o", "temp_output.bin"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if should_fail:
            # This test should fail
            if result.returncode != 0:
                print(f"   [PASS] Correctly detected error: {result.stderr.strip()}")
                return True
            else:
                print(f"   [FAIL] Should have detected error but succeeded")
                return False
        else:
            # This test should succeed
            if result.returncode == 0:
                print(f"   [PASS] Assembly completed successfully")
                return True
            else:
                print(f"   [FAIL] {result.stderr.strip()}")
                return False
            
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    finally:
        # Cleanup
        for file in [temp_file, Path("temp_output.bin")]:
            if file.exists():
                file.unlink()

def main():
    """Run basic functionality tests."""
    print("pyasm6502 - Quick Test Runner")
    print("=" * 50)
    
    tests = [
        # Basic instruction test
        ("""
!cpu 6502
* = $1000

start:
    lda #$42
    sta $0200
    rts
""", "Basic 6502 instructions"),
        
        # 65C02 specific instructions
        ("""
!cpu 65c02
* = $1000

start:
    stz $0200
    bra start
""", "65C02 specific instructions"),
        
        # Mathematical expressions
        ("""
!cpu 6502
* = $1000

value1 = 10
value2 = 20
result = value1 + value2

start:
    lda #result
    rts
""", "Mathematical expressions"),
        
        # Conditional assembly
        ("""
!cpu 6502
* = $1000

SYSTEM = 64

!if SYSTEM = 64
    lda #$01
!else
    lda #$02
!fi
    rts
""", "Conditional assembly"),
        
        # Macro system
        ("""
!cpu 6502
* = $1000

!macro push_reg reg {
    pha
    lda reg
    pha
}

start:
    +push_reg $0200
    rts
""", "Macro system"),
        
        # Error detection (should fail)
        ("""
!cpu 6502
* = $1000

start:
    lda undefined_symbol
    rts
""", "Error detection (should fail)", True),  # True indicates this should fail
    ]
    
    passed = 0
    total = len(tests)
    
    for test_data in tests:
        if len(test_data) == 3:
            source_code, description, should_fail = test_data
        else:
            source_code, description = test_data
            should_fail = False
        
        if run_assembler_test(source_code, description, should_fail):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[WARNING] Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
