#!/usr/bin/env python3
"""
CityPulse E2E Testing Legacy Assessment Tool

This tool analyzes existing test files to identify:
- Obsolete tests for removed features
- Broken tests that need fixing or removal
- Redundant tests across different test suites
- Tests that don't match current implementation
"""

import os
import json
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import subprocess

class LegacyTestAssessment:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.assessment_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "test_directories": [],
            "obsolete_tests": [],
            "broken_tests": [],
            "redundant_tests": [],
            "valid_tests": [],
            "recommendations": []
        }
        
    def analyze_test_structure(self) -> Dict[str, Any]:
        """Analyze the current test directory structure."""
        test_dirs = [
            "tests/",
            "__tests__/",
            "e2e-tests/",
            "tests/e2e-legacy/",
            "tests/integration/",
            "tests/unit/"
        ]
        
        structure = {}
        for test_dir in test_dirs:
            full_path = self.project_root / test_dir
            if full_path.exists():
                structure[test_dir] = self._scan_directory(full_path)
                
        self.assessment_results["test_directories"] = structure
        return structure
    
    def _scan_directory(self, directory: Path) -> Dict[str, Any]:
        """Scan a directory for test files and metadata."""
        result = {
            "path": str(directory),
            "exists": directory.exists(),
            "files": [],
            "subdirectories": [],
            "total_files": 0,
            "test_files": 0
        }
        
        if not directory.exists():
            return result
            
        for item in directory.rglob("*"):
            if item.is_file():
                result["total_files"] += 1
                file_info = {
                    "name": item.name,
                    "path": str(item.relative_to(self.project_root)),
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "is_test": self._is_test_file(item),
                    "language": self._detect_language(item)
                }
                
                if file_info["is_test"]:
                    result["test_files"] += 1
                    file_info.update(self._analyze_test_file(item))
                    
                result["files"].append(file_info)
            elif item.is_dir():
                result["subdirectories"].append(str(item.relative_to(directory)))
                
        return result
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Determine if a file is a test file."""
        test_patterns = [
            r"test_.*\.py$",
            r".*_test\.py$",
            r".*\.test\.(js|ts)$",
            r".*\.spec\.(js|ts)$",
            r"test.*\.(js|ts)$"
        ]
        
        return any(re.match(pattern, file_path.name) for pattern in test_patterns)
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect the programming language of a file."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown"
        }
        return extension_map.get(file_path.suffix, "unknown")
    
    def _analyze_test_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a test file for content and relevance."""
        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "dependencies": [],
            "api_endpoints": [],
            "ui_selectors": [],
            "potential_issues": []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if file_path.suffix == ".py":
                analysis.update(self._analyze_python_test(content))
            elif file_path.suffix in [".js", ".ts"]:
                analysis.update(self._analyze_javascript_test(content))
                
        except Exception as e:
            analysis["potential_issues"].append(f"Failed to read file: {str(e)}")
            
        return analysis
    
    def _analyze_python_test(self, content: str) -> Dict[str, Any]:
        """Analyze Python test file content."""
        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "api_endpoints": [],
            "potential_issues": []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        analysis["functions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef)
                        })
                elif isinstance(node, ast.ClassDef):
                    if "test" in node.name.lower():
                        analysis["classes"].append({
                            "name": node.name,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)
            
            # Look for API endpoint patterns
            api_patterns = [
                r'"/api/v1/[^"]*"',
                r"'/api/v1/[^']*'",
                r'"/v1/[^"]*"',
                r"'/v1/[^']*'"
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                analysis["api_endpoints"].extend(matches)
                
        except SyntaxError as e:
            analysis["potential_issues"].append(f"Python syntax error: {str(e)}")
        except Exception as e:
            analysis["potential_issues"].append(f"Analysis error: {str(e)}")
            
        return analysis
    
    def _analyze_javascript_test(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript test file content."""
        analysis = {
            "functions": [],
            "imports": [],
            "api_endpoints": [],
            "ui_selectors": [],
            "potential_issues": []
        }
        
        # Extract test functions
        test_patterns = [
            r"test\s*\(\s*['\"]([^'\"]*)['\"]",
            r"it\s*\(\s*['\"]([^'\"]*)['\"]",
            r"describe\s*\(\s*['\"]([^'\"]*)['\"]"
        ]
        
        for pattern in test_patterns:
            matches = re.findall(pattern, content)
            analysis["functions"].extend(matches)
        
        # Extract imports
        import_patterns = [
            r"import\s+.*\s+from\s+['\"]([^'\"]*)['\"]",
            r"require\s*\(\s*['\"]([^'\"]*)['\"]"
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            analysis["imports"].extend(matches)
        
        # Extract API endpoints
        api_patterns = [
            r'[\'\"]/api/v1/[^\'\"]*/[\'\"]*',
            r'[\'\"]/v1/[^\'\"]*/[\'\"]*'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            analysis["api_endpoints"].extend(matches)
        
        # Extract UI selectors
        selector_patterns = [
            r'[\'\"]\[data-testid=[^\]]*\][\'\"]*',
            r'[\'\"]\#[a-zA-Z][a-zA-Z0-9_-]*[\'\"]*',
            r'[\'\"]\.[a-zA-Z][a-zA-Z0-9_-]*[\'\"]*'
        ]
        
        for pattern in selector_patterns:
            matches = re.findall(pattern, content)
            analysis["ui_selectors"].extend(matches)
            
        return analysis
    
    def identify_obsolete_tests(self) -> List[Dict[str, Any]]:
        """Identify tests for features that no longer exist."""
        obsolete_tests = []
        
        # Check for tests referencing removed features
        removed_features = [
            "dashboard-mockups",
            "legacy-ui-components",
            "old-api-endpoints",
            "deprecated-models"
        ]
        
        for test_dir_info in self.assessment_results["test_directories"].values():
            for file_info in test_dir_info.get("files", []):
                if not file_info.get("is_test", False):
                    continue
                    
                issues = []
                
                # Check for references to removed features
                for feature in removed_features:
                    if feature in str(file_info):
                        issues.append(f"References removed feature: {feature}")
                
                # Check for broken imports
                for import_name in file_info.get("imports", []):
                    if self._is_broken_import(import_name):
                        issues.append(f"Broken import: {import_name}")
                
                if issues:
                    obsolete_tests.append({
                        "file": file_info["path"],
                        "issues": issues,
                        "recommendation": "REMOVE" if len(issues) > 2 else "FIX"
                    })
        
        self.assessment_results["obsolete_tests"] = obsolete_tests
        return obsolete_tests
    
    def _is_broken_import(self, import_name: str) -> bool:
        """Check if an import references a non-existent module."""
        # This is a simplified check - in practice, you'd want to verify
        # against the actual codebase structure
        broken_imports = [
            "legacy-api",
            "old-models",
            "deprecated-utils",
            "removed-components"
        ]
        
        return any(broken in import_name for broken in broken_imports)
    
    def identify_redundant_tests(self) -> List[Dict[str, Any]]:
        """Identify redundant tests across different test suites."""
        redundant_tests = []
        
        # Group tests by functionality
        test_groups = {}
        
        for test_dir_info in self.assessment_results["test_directories"].values():
            for file_info in test_dir_info.get("files", []):
                if not file_info.get("is_test", False):
                    continue
                
                # Group by API endpoints tested
                for endpoint in file_info.get("api_endpoints", []):
                    if endpoint not in test_groups:
                        test_groups[endpoint] = []
                    test_groups[endpoint].append(file_info["path"])
        
        # Find duplicates
        for endpoint, files in test_groups.items():
            if len(files) > 1:
                redundant_tests.append({
                    "endpoint": endpoint,
                    "files": files,
                    "recommendation": f"Consolidate tests for {endpoint}"
                })
        
        self.assessment_results["redundant_tests"] = redundant_tests
        return redundant_tests
    
    def generate_recommendations(self) -> List[str]:
        """Generate cleanup recommendations based on analysis."""
        recommendations = []
        
        # Obsolete tests recommendations
        if self.assessment_results["obsolete_tests"]:
            recommendations.append(
                f"Remove {len(self.assessment_results['obsolete_tests'])} obsolete test files"
            )
        
        # Redundant tests recommendations
        if self.assessment_results["redundant_tests"]:
            recommendations.append(
                f"Consolidate {len(self.assessment_results['redundant_tests'])} redundant test groups"
            )
        
        # Structure recommendations
        recommendations.extend([
            "Migrate valuable tests from tests/e2e-legacy/ to e2e-tests/",
            "Consolidate Jest and pytest configurations",
            "Implement automated test relevance checking",
            "Set up test coverage reporting",
            "Create test maintenance automation"
        ])
        
        self.assessment_results["recommendations"] = recommendations
        return recommendations
    
    def save_assessment_report(self, output_path: str = None) -> str:
        """Save the assessment report to a file."""
        if output_path is None:
            output_path = f"e2e-tests/legacy-cleanup/assessment-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        output_file = self.project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.assessment_results, f, indent=2)
        
        return str(output_file)
    
    def run_full_assessment(self) -> Dict[str, Any]:
        """Run the complete legacy test assessment."""
        print("🔍 Starting CityPulse E2E Test Legacy Assessment...")
        
        print("📁 Analyzing test directory structure...")
        self.analyze_test_structure()
        
        print("🗑️  Identifying obsolete tests...")
        self.identify_obsolete_tests()
        
        print("🔄 Identifying redundant tests...")
        self.identify_redundant_tests()
        
        print("💡 Generating recommendations...")
        self.generate_recommendations()
        
        print("📊 Saving assessment report...")
        report_path = self.save_assessment_report()
        
        print(f"✅ Assessment complete! Report saved to: {report_path}")
        
        return self.assessment_results

def main():
    """Main entry point for the assessment tool."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    assessor = LegacyTestAssessment(project_root)
    results = assessor.run_full_assessment()
    
    # Print summary
    print("\n📋 Assessment Summary:")
    print(f"   Test directories found: {len(results['test_directories'])}")
    print(f"   Obsolete tests: {len(results['obsolete_tests'])}")
    print(f"   Redundant tests: {len(results['redundant_tests'])}")
    print(f"   Recommendations: {len(results['recommendations'])}")
    
    print("\n🎯 Top Recommendations:")
    for i, rec in enumerate(results['recommendations'][:5], 1):
        print(f"   {i}. {rec}")

if __name__ == "__main__":
    main()
