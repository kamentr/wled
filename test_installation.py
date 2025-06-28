#!/usr/bin/env python3
"""Test script to verify WLED Controller installation."""

import sys
import importlib.util

def check_dependency(module_name, package_name=None):
    """Check if a dependency is installed."""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False

def main():
    """Run installation tests."""
    print("WLED Controller - Installation Test")
    print("=" * 40)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} is compatible")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor}.{python_version.micro} is too old. Need 3.8+")
        return False
    
    print("\nChecking dependencies:")
    dependencies = [
        ('requests', 'requests'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('jinja2', 'jinja2'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_installed = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_installed = False
    
    print("\nChecking project files:")
    import os
    
    required_files = [
        'src/__init__.py',
        'src/wled_client.py',
        'src/app.py',
        'static/app.js',
        'templates/index.html',
        'main.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} is missing")
            all_installed = False
    
    print("\nTesting imports:")
    try:
        from src.wled_client import WLEDClient
        print("✓ WLEDClient can be imported")
    except ImportError as e:
        print(f"✗ Failed to import WLEDClient: {e}")
        all_installed = False
    
    try:
        from src.app import app
        print("✓ FastAPI app can be imported")
    except ImportError as e:
        print(f"✗ Failed to import FastAPI app: {e}")
        all_installed = False
    
    print("\n" + "=" * 40)
    if all_installed:
        print("✓ All tests passed! Installation is complete.")
        print("\nTo start the application:")
        print("1. Create a .env file with your WLED device configuration")
        print("2. Run: python main.py")
        print("3. Open http://127.0.0.1:8000 in your browser")
        return True
    else:
        print("✗ Some tests failed. Please check the issues above.")
        print("\nTo fix missing dependencies:")
        print("pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 