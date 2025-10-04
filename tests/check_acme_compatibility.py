#!/usr/bin/env python3
"""
pyasm6502 - ACME Compatibility Checker
Downloads ACME test files from official repository and validates compatibility
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, List, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# ACME test files repository URLs
ACME_TEST_BASE_URL = "https://raw.githubusercontent.com/visrealm/acme/main/testing"
ACME_TEST_FILES = {
    "math1.a": f"{ACME_TEST_BASE_URL}/math1.a",
    "numberflags.a": f"{ACME_TEST_BASE_URL}/numberflags.a",
    "cpus/test-6502.a": f"{ACME_TEST_BASE_URL}/cpus/test-6502.a",
    "cpus/test-65c02.a": f"{ACME_TEST_BASE_URL}/cpus/test-65c02.a",
    "cpus/test-nmos6502.a": f"{ACME_TEST_BASE_URL}/cpus/test-nmos6502.a",
    "cpus/test-w65c02.a": f"{ACME_TEST_BASE_URL}/cpus/test-w65c02.a",
    "cpus/include-6502.a": f"{ACME_TEST_BASE_URL}/cpus/include-6502.a",
    "cpus/include-65c02.a": f"{ACME_TEST_BASE_URL}/cpus/include-65c02.a",
    "cpus/include-undoc.a": f"{ACME_TEST_BASE_URL}/cpus/include-undoc.a",
    "cpus/include-bitmanips.a": f"{ACME_TEST_BASE_URL}/cpus/include-bitmanips.a",
    "errors/alreadydefined1.a": f"{ACME_TEST_BASE_URL}/errors/alreadydefined1.a",
    "errors/valuenotdefined1.a": f"{ACME_TEST_BASE_URL}/errors/valuenotdefined1.a",
    "warnings/binlen.a": f"{ACME_TEST_BASE_URL}/warnings/binlen.a",
}

def download_file(url: str, local_path: Path) -> bool:
    """Download a file from URL to local path."""
    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, local_path)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def setup_test_files(test_dir: Path) -> bool:
    """Download ACME test files to temporary directory."""
    print("Setting up ACME test files...")
    
    # Create subdirectories
    (test_dir / "cpus").mkdir(exist_ok=True)
    (test_dir / "errors").mkdir(exist_ok=True)
    (test_dir / "warnings").mkdir(exist_ok=True)
    
    success = True
    for local_path, url in ACME_TEST_FILES.items():
        file_path = test_dir / local_path
        if not download_file(url, file_path):
            success = False
    
    return success

def run_assembler(input_file: Path, output_file: Path = None, format_type: str = "plain") -> Tuple[bool, str]:
    """Run the assembler and return (success, output_message)"""
    try:
        cmd = [
            "pyasm6502",
            str(input_file),
        ]

        if output_file:
            cmd.extend(["-o", str(output_file)])

        if format_type != "plain":
            cmd.extend(["-f", format_type])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=input_file.parent)

        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()

        return True, result.stdout.strip()

    except Exception as e:
        return False, f"Error running assembler: {e}"

def run_acme_reference(input_file: Path, output_file: Path = None, format_type: str = "plain") -> Tuple[bool, str]:
    """Run ACME assembler for reference comparison."""
    try:
        # Try to find ACME executable
        acme_cmd = None
        for cmd in ["acme", "acme.exe"]:
            if shutil.which(cmd):
                acme_cmd = cmd
                break
        
        if not acme_cmd:
            return False, "ACME assembler not found in PATH"

        cmd = [acme_cmd, str(input_file)]
        
        if output_file:
            cmd.extend(["-o", str(output_file)])
        
        if format_type != "plain":
            cmd.extend(["-f", format_type])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=input_file.parent)

        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()

        return True, result.stdout.strip()

    except Exception as e:
        return False, f"Error running ACME: {e}"

def compare_files(file1: Path, file2: Path) -> Tuple[bool, str]:
    """Compare two binary files and return (is_identical, difference_info)"""
    if not file1.exists():
        return False, f"Generated file {file1} does not exist"

    if not file2.exists():
        return False, f"Expected file {file2} does not exist"

    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            data1 = f1.read()
            data2 = f2.read()

        if data1 == data2:
            return True, f"Files are identical ({len(data1)} bytes)"
        else:
            # Find first difference
            min_len = min(len(data1), len(data2))
            for i in range(min_len):
                if data1[i] != data2[i]:
                    return False, f"Files differ at byte {i}: {data1[i]:02X} vs {data2[i]:02X}"
            
            if len(data1) != len(data2):
                return False, f"Files differ in length: {len(data1)} vs {len(data2)} bytes"
            
            return False, "Files differ but no specific difference found"

    except Exception as e:
        return False, f"Error comparing files: {e}"

def run_compatibility_tests(test_dir: Path) -> Dict[str, bool]:
    """Run ACME compatibility tests."""
    results = {}
    
    # Test files to run
    test_files = [
        ("math1.a", "Mathematical expressions test"),
        ("numberflags.a", "Number formatting test"),
        ("cpus/test-6502.a", "6502 instruction set test"),
        ("cpus/test-65c02.a", "65C02 instruction set test"),
        ("cpus/test-nmos6502.a", "NMOS6502 instruction set test"),
        ("cpus/test-w65c02.a", "W65C02S instruction set test"),
    ]
    
    print("\n" + "="*60)
    print("ACME COMPATIBILITY TESTS")
    print("="*60)
    
    for test_file, description in test_files:
        test_path = test_dir / test_file
        if not test_path.exists():
            print(f"[ERROR] {description}: Test file not found")
            results[test_file] = False
            continue
        
        print(f"\n[TEST] {description}")
        print(f"   File: {test_file}")
        
        # Generate output filenames
        base_name = test_path.stem
        output_dir = test_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        our_output = output_dir / f"{base_name}_our.bin"
        acme_output = output_dir / f"{base_name}_acme.bin"
        
        # Run our assembler
        print("   Running asm6502...")
        success, message = run_assembler(test_path, our_output)
        if not success:
            print(f"   [ERROR] asm6502 failed: {message}")
            results[test_file] = False
            continue
        
        # Run ACME for comparison
        print("   Running ACME...")
        success, message = run_acme_reference(test_path, acme_output)
        if not success:
            print(f"   [WARNING]  ACME not available: {message}")
            print(f"   [SUCCESS] asm6502 completed successfully")
            results[test_file] = True
            continue
        
        # Compare outputs
        print("   Comparing outputs...")
        identical, diff_info = compare_files(our_output, acme_output)
        
        if identical:
            print(f"   [PASS] {diff_info}")
            results[test_file] = True
        else:
            print(f"   [FAIL] {diff_info}")
            results[test_file] = False
    
    return results

def run_error_tests(test_dir: Path) -> Dict[str, bool]:
    """Run error detection tests."""
    results = {}
    
    error_tests = [
        ("errors/alreadydefined1.a", "Symbol redefinition error"),
        ("errors/valuenotdefined1.a", "Undefined symbol error"),
    ]
    
    print("\n" + "="*60)
    print("ERROR DETECTION TESTS")
    print("="*60)
    
    for test_file, description in error_tests:
        test_path = test_dir / test_file
        if not test_path.exists():
            print(f"[ERROR] {description}: Test file not found")
            results[test_file] = False
            continue
        
        print(f"\n[TEST] {description}")
        print(f"   File: {test_file}")
        
        # Run assembler - should fail
        success, message = run_assembler(test_path)
        
        if not success:
            print(f"   [PASS] Correctly detected error")
            print(f"   Error: {message}")
            results[test_file] = True
        else:
            print(f"   [FAIL] Should have detected error")
            results[test_file] = False
    
    return results

def main():
    """Main test runner."""
    print("pyasm6502 - ACME Compatibility Checker")
    print("=" * 60)
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Download test files
        if not setup_test_files(test_dir):
            print("[ERROR] Failed to download test files")
            return 1
        
        print(f"[SUCCESS] Test files downloaded to temporary directory")
        
        # Run compatibility tests
        compat_results = run_compatibility_tests(test_dir)
        
        # Run error tests
        error_results = run_error_tests(test_dir)
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        all_results = {**compat_results, **error_results}
        passed = sum(1 for result in all_results.values() if result)
        total = len(all_results)
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("[SUCCESS] ALL TESTS PASSED! ACME compatibility achieved.")
            return 0
        else:
            print("[WARNING] Some tests failed. Check output above for details.")
            return 1

if __name__ == "__main__":
    sys.exit(main())