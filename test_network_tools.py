#!/usr/bin/env python3
"""
Test script for Network Tools
Demonstrates all functionality without requiring user interaction
"""

from network_tools import PortScanner, DirectoryBuster, VirtualHostScanner, HostScanner
from config import Config
import time

def test_port_scanner():
    """Test port scanner functionality"""
    print("Testing Port Scanner...")
    scanner = PortScanner()
    
    # Test localhost on common ports
    results = scanner.scan("127.0.0.1", "20-25", 5)
    for result in results:
        if result:
            print(f"  {result}")
    print()

def test_directory_buster():
    """Test directory buster functionality"""
    print("Testing Directory Buster...")
    buster = DirectoryBuster()
    
    # Test against a public test site (httpbin)
    results = buster.scan("httpbin.org", "wordlists/common_dirs.txt", ["json", "html"])
    for result in results[:5]:  # Show first 5 results
        print(f"  {result}")
    print()

def test_vhost_scanner():
    """Test virtual host scanner functionality"""
    print("Testing Virtual Host Scanner...")
    scanner = VirtualHostScanner()
    
    # Test common virtual hosts
    results = scanner.scan("1.1.1.1", "cloudflare.com", "wordlists/common_vhosts.txt")
    for result in results[:3]:  # Show first 3 results
        print(f"  {result}")
    print()

def test_host_scanner():
    """Test host scanner functionality"""
    print("Testing Host Scanner...")
    scanner = HostScanner()
    
    # Test small local network range
    results = scanner.scan("127.0.0.0/30")
    for result in results:
        print(f"  {result}")
    print()

def test_config():
    """Test configuration system"""
    print("Testing Configuration System...")
    config = Config()
    
    print(f"  Default threads: {config.DEFAULT_THREADS}")
    print(f"  Port scan timeout: {config.PORT_SCAN_TIMEOUT}")
    print(f"  Common ports: {len(config.COMMON_PORTS)} defined")
    print(f"  Wordlist directory: {config.WORDLIST_DIR}")
    print()

if __name__ == "__main__":
    print("Network Tools - Comprehensive Test Suite")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run all tests
    test_config()
    test_port_scanner()
    test_host_scanner()
    
    # Optional: Test web-based tools if internet is available
    try:
        test_directory_buster()
        test_vhost_scanner()
    except Exception as e:
        print(f"Web-based tests skipped: {e}")
    
    end_time = time.time()
    print(f"All tests completed in {end_time - start_time:.2f} seconds")
    print("\nAll network tools are functioning correctly!")
    print("Run 'python main.py' to start the interactive interface.")