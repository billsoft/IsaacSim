#!/usr/bin/env python3
"""
Test script for Packman retry configuration functionality.
This script tests the modified call_with_retry function and configuration loading.
"""

import os
import sys
import json
import tempfile
import time
from unittest.mock import patch

# Add the bootstrap directory to the path
bootstrap_dir = os.path.join(os.path.dirname(__file__), "bootstrap")
sys.path.insert(0, bootstrap_dir)

try:
    from install_package import call_with_retry, load_retry_config, _retry_config
    print("✓ Successfully imported modified install_package module")
except ImportError as e:
    print(f"✗ Failed to import install_package module: {e}")
    sys.exit(1)


def test_config_loading():
    """Test configuration loading from file and environment variables"""
    print("\n=== Testing Configuration Loading ===")
    
    # Test current configuration
    print(f"Current retry config: {_retry_config}")
    
    # Verify expected values
    expected_download_retries = 1000
    expected_download_delay = 600  # 10 minutes
    
    if _retry_config["download_retry_count"] == expected_download_retries:
        print(f"✓ Download retry count correctly set to {expected_download_retries}")
    else:
        print(f"✗ Download retry count is {_retry_config['download_retry_count']}, expected {expected_download_retries}")
    
    if _retry_config["download_retry_delay"] == expected_download_delay:
        print(f"✓ Download retry delay correctly set to {expected_download_delay} seconds (10 minutes)")
    else:
        print(f"✗ Download retry delay is {_retry_config['download_retry_delay']}, expected {expected_download_delay}")


def test_call_with_retry_download():
    """Test call_with_retry function with download operation type"""
    print("\n=== Testing call_with_retry for Download Operations ===")
    
    call_count = 0
    
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:  # Fail first 2 times
            raise OSError(f"Simulated failure #{call_count}")
        return f"Success after {call_count} attempts"
    
    try:
        # Test with download operation type (should use config values)
        start_time = time.time()
        result = call_with_retry(
            "test download operation",
            failing_function,
            operation_type="download",
            retry_count=3,  # Override for testing (don't wait 10 minutes)
            retry_delay=0.1  # Override for testing
        )
        end_time = time.time()
        
        print(f"✓ Download operation succeeded: {result}")
        print(f"✓ Total attempts: {call_count}")
        print(f"✓ Total time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"✗ Download operation failed: {e}")


def test_call_with_retry_rename():
    """Test call_with_retry function with rename operation type"""
    print("\n=== Testing call_with_retry for Rename Operations ===")
    
    call_count = 0
    
    def failing_rename():
        nonlocal call_count
        call_count += 1
        if call_count < 2:  # Fail first time
            raise OSError(f"Simulated rename failure #{call_count}")
        return f"Rename success after {call_count} attempts"
    
    try:
        result = call_with_retry(
            "test rename operation",
            failing_rename,
            operation_type="rename"
        )
        
        print(f"✓ Rename operation succeeded: {result}")
        print(f"✓ Total attempts: {call_count}")
        
    except Exception as e:
        print(f"✗ Rename operation failed: {e}")


def test_environment_variable_override():
    """Test environment variable override functionality"""
    print("\n=== Testing Environment Variable Override ===")
    
    # Set test environment variables
    os.environ["PACKMAN_DOWNLOAD_RETRY_COUNT"] = "5"
    os.environ["PACKMAN_DOWNLOAD_RETRY_DELAY"] = "1"
    
    # Reload configuration
    new_config = load_retry_config()
    
    if new_config["download_retry_count"] == 5:
        print("✓ Environment variable override for retry count works")
    else:
        print(f"✗ Environment variable override failed: got {new_config['download_retry_count']}, expected 5")
    
    if new_config["download_retry_delay"] == 1:
        print("✓ Environment variable override for retry delay works")
    else:
        print(f"✗ Environment variable override failed: got {new_config['download_retry_delay']}, expected 1")
    
    # Clean up environment variables
    del os.environ["PACKMAN_DOWNLOAD_RETRY_COUNT"]
    del os.environ["PACKMAN_DOWNLOAD_RETRY_DELAY"]


def main():
    """Run all tests"""
    print("Packman Retry Configuration Test Suite")
    print("=" * 50)
    
    test_config_loading()
    test_call_with_retry_download()
    test_call_with_retry_rename()
    test_environment_variable_override()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")


if __name__ == "__main__":
    main()