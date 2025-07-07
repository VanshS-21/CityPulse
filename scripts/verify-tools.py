#!/usr/bin/env python3
"""
Quick verification script for CityPulse testing tools.
Checks if all required tools are available without installing anything.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_command(command, name):
    """Check if a command is available."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {name}: Available")
            return True
        else:
            print(f"❌ {name}: Command failed")
            return False
    except FileNotFoundError:
        print(f"❌ {name}: Not found")
        return False
    except subprocess.TimeoutExpired:
        print(f"⚠️ {name}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def check_python_package(package, name=None):
    """Check if a Python package is available."""
    if name is None:
        name = package
    
    try:
        result = subprocess.run([
            sys.executable, "-c", f"import {package}; print('OK')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ {name}: Available")
            return True
        else:
            print(f"❌ {name}: Import failed")
            return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def check_file_exists(file_path, name):
    """Check if a file exists."""
    if Path(file_path).exists():
        print(f"✅ {name}: Found")
        return True
    else:
        print(f"❌ {name}: Missing")
        return False

def main():
    """Main verification function."""
    print("🔍 CityPulse Testing Tools Verification")
    print("=" * 50)
    
    results = []
    
    # Check system requirements
    print("\n📋 System Requirements:")
    results.append(check_command(['python', '--version'], 'Python'))
    results.append(check_command(['node', '--version'], 'Node.js'))
    results.append(check_command(['npm', '--version'], 'npm'))
    
    # Check Python testing tools
    print("\n🐍 Python Testing Tools:")
    results.append(check_python_package('pytest'))
    results.append(check_python_package('requests'))
    results.append(check_python_package('psutil'))
    
    # Check if we can import Google Cloud libraries
    print("\n☁️ Google Cloud Libraries:")
    results.append(check_python_package('google.cloud.bigquery', 'BigQuery'))
    results.append(check_python_package('google.cloud.firestore', 'Firestore'))
    results.append(check_python_package('google.cloud.pubsub', 'Pub/Sub'))
    
    # Check Apache Beam
    print("\n🌊 Apache Beam:")
    results.append(check_python_package('apache_beam', 'Apache Beam'))
    
    # Check Node.js tools
    print("\n📦 Node.js Tools:")
    results.append(check_command(['npx', 'jest', '--version'], 'Jest'))
    results.append(check_command(['npx', 'playwright', '--version'], 'Playwright'))
    
    # Check configuration files
    print("\n⚙️ Configuration Files:")
    results.append(check_file_exists('package.json', 'package.json'))
    results.append(check_file_exists('requirements.txt', 'requirements.txt'))
    results.append(check_file_exists('requirements-test.txt', 'requirements-test.txt'))
    results.append(check_file_exists('jest.config.js', 'jest.config.js'))
    results.append(check_file_exists('playwright.config.ts', 'playwright.config.ts'))
    
    # Check test directories
    print("\n📁 Test Structure:")
    results.append(check_file_exists('tests/', 'tests directory'))
    results.append(check_file_exists('tests/unit/', 'unit tests'))
    results.append(check_file_exists('tests/integration/', 'integration tests'))
    results.append(check_file_exists('tests/e2e/', 'e2e tests'))
    results.append(check_file_exists('tests/conftest.py', 'pytest config'))
    
    # Summary
    print("\n" + "=" * 50)
    total_checks = len(results)
    passed_checks = sum(results)
    
    print(f"📊 Summary: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 All tools are ready!")
        print("\nYou can run tests with:")
        print("  python tests/test_runner.py")
        print("  npm test")
        print("  npx playwright test")
        return True
    else:
        print("⚠️ Some tools are missing or not configured.")
        print("\nTo install missing tools, run:")
        print("  python scripts/setup-testing-tools.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
