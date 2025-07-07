#!/usr/bin/env python3
"""
CityPulse Testing Framework Setup and Verification Script
Downloads and verifies all required tools for the comprehensive testing framework.
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestingToolsSetup:
    """Setup and verify testing tools for CityPulse."""
    
    def __init__(self):
        """Initialize the setup manager."""
        self.project_root = Path.cwd()
        self.python_version = sys.version_info
        self.node_version = None
        self.npm_version = None
        self.results = {
            "python_tools": {},
            "node_tools": {},
            "system_tools": {},
            "verification": {}
        }
    
    def check_system_requirements(self) -> bool:
        """Check system requirements."""
        logger.info("🔍 Checking system requirements...")
        
        # Check Python version
        if self.python_version < (3, 11):
            logger.error(f"❌ Python 3.11+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
        else:
            logger.info(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.node_version = result.stdout.strip()
                logger.info(f"✅ Node.js {self.node_version}")
            else:
                logger.error("❌ Node.js not found")
                return False
        except FileNotFoundError:
            logger.error("❌ Node.js not installed")
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.npm_version = result.stdout.strip()
                logger.info(f"✅ npm {self.npm_version}")
            else:
                logger.error("❌ npm not found")
                return False
        except FileNotFoundError:
            logger.error("❌ npm not installed")
            return False
        
        return True
    
    def install_python_dependencies(self) -> bool:
        """Install Python testing dependencies."""
        logger.info("📦 Installing Python testing dependencies...")
        
        try:
            # Install main requirements first
            if (self.project_root / "requirements.txt").exists():
                logger.info("Installing main requirements...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"❌ Failed to install main requirements: {result.stderr}")
                    return False
            
            # Install test requirements
            if (self.project_root / "requirements-test.txt").exists():
                logger.info("Installing test requirements...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"❌ Failed to install test requirements: {result.stderr}")
                    return False
                else:
                    logger.info("✅ Python test dependencies installed")
            
            # Install Playwright browsers
            logger.info("Installing Playwright browsers...")
            result = subprocess.run([
                sys.executable, "-m", "playwright", "install"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Playwright browser installation had issues: {result.stderr}")
            else:
                logger.info("✅ Playwright browsers installed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing Python dependencies: {e}")
            return False
    
    def install_node_dependencies(self) -> bool:
        """Install Node.js testing dependencies."""
        logger.info("📦 Installing Node.js testing dependencies...")
        
        try:
            # Install npm dependencies
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to install npm dependencies: {result.stderr}")
                return False
            else:
                logger.info("✅ Node.js dependencies installed")
            
            # Install Playwright browsers via npm
            result = subprocess.run(['npx', 'playwright', 'install'], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Playwright browser installation via npm had issues: {result.stderr}")
            else:
                logger.info("✅ Playwright browsers installed via npm")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing Node.js dependencies: {e}")
            return False
    
    def verify_python_tools(self) -> Dict[str, bool]:
        """Verify Python testing tools."""
        logger.info("🔍 Verifying Python testing tools...")
        
        tools_to_check = [
            'pytest',
            'playwright',
            'requests',
            'psutil',
            'cryptography',
            'bcrypt',
            'coverage',
            'bandit',
            'safety',
            'google-cloud-bigquery',
            'google-cloud-firestore',
            'apache-beam'
        ]
        
        results = {}
        
        for tool in tools_to_check:
            try:
                result = subprocess.run([
                    sys.executable, "-c", f"import {tool.replace('-', '_')}; print('OK')"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    results[tool] = True
                    logger.info(f"✅ {tool}")
                else:
                    results[tool] = False
                    logger.error(f"❌ {tool} - {result.stderr.strip()}")
                    
            except Exception as e:
                results[tool] = False
                logger.error(f"❌ {tool} - {e}")
        
        self.results["python_tools"] = results
        return results
    
    def verify_node_tools(self) -> Dict[str, bool]:
        """Verify Node.js testing tools."""
        logger.info("🔍 Verifying Node.js testing tools...")
        
        tools_to_check = [
            'jest',
            '@playwright/test',
            '@testing-library/react',
            '@testing-library/jest-dom',
            'jest-axe',
            '@axe-core/playwright',
            'msw'
        ]
        
        results = {}
        
        for tool in tools_to_check:
            try:
                # Check if package is installed
                result = subprocess.run([
                    'npm', 'list', tool, '--depth=0'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    results[tool] = True
                    logger.info(f"✅ {tool}")
                else:
                    results[tool] = False
                    logger.error(f"❌ {tool} not found")
                    
            except Exception as e:
                results[tool] = False
                logger.error(f"❌ {tool} - {e}")
        
        self.results["node_tools"] = results
        return results
    
    def verify_test_commands(self) -> Dict[str, bool]:
        """Verify test commands work."""
        logger.info("🔍 Verifying test commands...")
        
        commands_to_check = [
            (['python', '-m', 'pytest', '--version'], 'pytest'),
            (['npx', 'jest', '--version'], 'jest'),
            (['npx', 'playwright', '--version'], 'playwright'),
            (['python', '-c', 'import google.cloud.bigquery; print("BigQuery OK")'], 'bigquery'),
            (['python', '-c', 'import google.cloud.firestore; print("Firestore OK")'], 'firestore'),
            (['python', '-c', 'import apache_beam; print("Beam OK")'], 'apache_beam'),
        ]
        
        results = {}
        
        for command, name in commands_to_check:
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    results[name] = True
                    logger.info(f"✅ {name} command works")
                else:
                    results[name] = False
                    logger.error(f"❌ {name} command failed: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                results[name] = False
                logger.error(f"❌ {name} command timed out")
            except Exception as e:
                results[name] = False
                logger.error(f"❌ {name} command error: {e}")
        
        self.results["verification"] = results
        return results
    
    def create_test_directories(self) -> bool:
        """Create necessary test directories."""
        logger.info("📁 Creating test directories...")
        
        directories = [
            "test-reports",
            "test-results",
            "coverage",
            "tests/fixtures",
            "tests/mocks",
            "tests/utils"
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created {directory}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating directories: {e}")
            return False
    
    def run_sample_tests(self) -> Dict[str, bool]:
        """Run sample tests to verify everything works."""
        logger.info("🧪 Running sample tests...")
        
        test_results = {}
        
        # Test pytest
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "--version"
            ], capture_output=True, text=True, timeout=30)
            
            test_results["pytest"] = result.returncode == 0
            if result.returncode == 0:
                logger.info("✅ pytest working")
            else:
                logger.error(f"❌ pytest failed: {result.stderr}")
                
        except Exception as e:
            test_results["pytest"] = False
            logger.error(f"❌ pytest error: {e}")
        
        # Test Jest
        try:
            result = subprocess.run([
                'npx', 'jest', '--version'
            ], capture_output=True, text=True, timeout=30)
            
            test_results["jest"] = result.returncode == 0
            if result.returncode == 0:
                logger.info("✅ Jest working")
            else:
                logger.error(f"❌ Jest failed: {result.stderr}")
                
        except Exception as e:
            test_results["jest"] = False
            logger.error(f"❌ Jest error: {e}")
        
        # Test Playwright
        try:
            result = subprocess.run([
                'npx', 'playwright', '--version'
            ], capture_output=True, text=True, timeout=30)
            
            test_results["playwright"] = result.returncode == 0
            if result.returncode == 0:
                logger.info("✅ Playwright working")
            else:
                logger.error(f"❌ Playwright failed: {result.stderr}")
                
        except Exception as e:
            test_results["playwright"] = False
            logger.error(f"❌ Playwright error: {e}")
        
        return test_results
    
    def generate_report(self) -> None:
        """Generate setup verification report."""
        logger.info("📊 Generating setup report...")
        
        # Calculate success rates
        python_success = sum(self.results["python_tools"].values())
        python_total = len(self.results["python_tools"])
        
        node_success = sum(self.results["node_tools"].values())
        node_total = len(self.results["node_tools"])
        
        verification_success = sum(self.results["verification"].values())
        verification_total = len(self.results["verification"])
        
        # Create report
        report = {
            "timestamp": subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            "system_info": {
                "platform": platform.platform(),
                "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
                "node_version": self.node_version,
                "npm_version": self.npm_version
            },
            "summary": {
                "python_tools": f"{python_success}/{python_total}",
                "node_tools": f"{node_success}/{node_total}",
                "verification": f"{verification_success}/{verification_total}",
                "overall_success": python_success == python_total and node_success == node_total and verification_success == verification_total
            },
            "details": self.results
        }
        
        # Save report
        report_path = self.project_root / "test-reports" / "setup-verification.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("CITYPULSE TESTING FRAMEWORK SETUP REPORT")
        print("="*60)
        print(f"Python Tools: {python_success}/{python_total} ({'✅' if python_success == python_total else '❌'})")
        print(f"Node.js Tools: {node_success}/{node_total} ({'✅' if node_success == node_total else '❌'})")
        print(f"Verification: {verification_success}/{verification_total} ({'✅' if verification_success == verification_total else '❌'})")
        print(f"Overall Status: {'✅ SUCCESS' if report['summary']['overall_success'] else '❌ ISSUES FOUND'}")
        print(f"Report saved to: {report_path}")
        print("="*60)
    
    def run_setup(self) -> bool:
        """Run complete setup process."""
        logger.info("🚀 Starting CityPulse testing framework setup...")
        
        # Check system requirements
        if not self.check_system_requirements():
            logger.error("❌ System requirements not met")
            return False
        
        # Create directories
        if not self.create_test_directories():
            logger.error("❌ Failed to create test directories")
            return False
        
        # Install dependencies
        if not self.install_python_dependencies():
            logger.error("❌ Failed to install Python dependencies")
            return False
        
        if not self.install_node_dependencies():
            logger.error("❌ Failed to install Node.js dependencies")
            return False
        
        # Verify installations
        self.verify_python_tools()
        self.verify_node_tools()
        self.verify_test_commands()
        
        # Run sample tests
        sample_results = self.run_sample_tests()
        self.results["sample_tests"] = sample_results
        
        # Generate report
        self.generate_report()
        
        # Check if setup was successful
        all_python_ok = all(self.results["python_tools"].values())
        all_node_ok = all(self.results["node_tools"].values())
        all_verification_ok = all(self.results["verification"].values())
        
        success = all_python_ok and all_node_ok and all_verification_ok
        
        if success:
            logger.info("🎉 Testing framework setup completed successfully!")
        else:
            logger.error("❌ Testing framework setup completed with issues. Check the report for details.")
        
        return success


def main():
    """Main function."""
    setup = TestingToolsSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 All testing tools are ready!")
        print("You can now run tests using:")
        print("  - python tests/test_runner.py")
        print("  - npm test")
        print("  - npx playwright test")
    else:
        print("\n❌ Setup completed with issues. Please check the report and fix any problems.")
        sys.exit(1)


if __name__ == "__main__":
    main()
