#!/usr/bin/env python3
"""
CityPulse Codebase Integration & Cohesion Analyzer
Performs comprehensive analysis of code integration and identifies issues.
"""

import ast
import os
import re
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any
import subprocess

class CodebaseAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.python_files = []
        self.typescript_files = []
        self.dependencies = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)
        self.file_metrics = {}
        self.issues = []
        
    def scan_files(self):
        """Scan for Python and TypeScript files."""
        print("🔍 Scanning codebase files...")
        
        # Python files
        for pattern in ["**/*.py", "*.py"]:
            for file_path in self.root_path.glob(pattern):
                if self._should_include_file(file_path):
                    self.python_files.append(file_path)
        
        # TypeScript files
        for pattern in ["**/*.ts", "**/*.tsx", "*.ts", "*.tsx"]:
            for file_path in self.root_path.glob(pattern):
                if self._should_include_file(file_path):
                    self.typescript_files.append(file_path)
        
        print(f"Found {len(self.python_files)} Python files")
        print(f"Found {len(self.typescript_files)} TypeScript files")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in analysis."""
        exclude_patterns = [
            "node_modules", ".git", "__pycache__", ".pytest_cache",
            "venv", ".venv", "dist", "build", ".next"
        ]
        
        path_str = str(file_path)
        return not any(pattern in path_str for pattern in exclude_patterns)
    
    def analyze_python_dependencies(self):
        """Analyze Python import dependencies."""
        print("🔗 Analyzing Python dependencies...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                imports = self._extract_python_imports(tree)
                
                relative_path = str(file_path.relative_to(self.root_path))
                self.dependencies[relative_path] = imports
                
                # Build reverse dependencies
                for imp in imports:
                    self.reverse_dependencies[imp].add(relative_path)
                
                # Calculate basic metrics
                self.file_metrics[relative_path] = {
                    'lines': len(content.splitlines()),
                    'imports': len(imports),
                    'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    'complexity': self._calculate_complexity(tree)
                }
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def analyze_typescript_dependencies(self):
        """Analyze TypeScript import dependencies."""
        print("🔗 Analyzing TypeScript dependencies...")
        
        for file_path in self.typescript_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = self._extract_typescript_imports(content)
                
                relative_path = str(file_path.relative_to(self.root_path))
                self.dependencies[relative_path] = imports
                
                # Build reverse dependencies
                for imp in imports:
                    self.reverse_dependencies[imp].add(relative_path)
                
                # Calculate basic metrics
                self.file_metrics[relative_path] = {
                    'lines': len(content.splitlines()),
                    'imports': len(imports),
                    'exports': len(re.findall(r'export\s+', content)),
                    'functions': len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(', content)),
                    'interfaces': len(re.findall(r'interface\s+\w+', content)),
                    'complexity': len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\bswitch\b', content))
                }
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    def _extract_python_imports(self, tree: ast.AST) -> Set[str]:
        """Extract import statements from Python AST."""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    
    def _extract_typescript_imports(self, content: str) -> Set[str]:
        """Extract import statements from TypeScript content."""
        imports = set()
        
        # Match import statements
        import_patterns = [
            r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",
            r"import\s+['\"]([^'\"]+)['\"]",
            r"require\(['\"]([^'\"]+)['\"]\)"
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.update(matches)
        
        return imports
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def detect_orphaned_files(self) -> List[str]:
        """Detect files with minimal connections."""
        print("🔍 Detecting orphaned files...")
        
        orphaned = []
        
        for file_path, deps in self.dependencies.items():
            # Check if file has very few dependencies and dependents
            dependents = len(self.reverse_dependencies.get(file_path, set()))
            dependencies = len(deps)
            
            if dependencies <= 1 and dependents <= 1:
                # Check if it's a main/entry file (these are expected to be orphaned)
                if not any(name in file_path.lower() for name in ['main', 'index', '__init__', 'app']):
                    orphaned.append(file_path)
                    self.issues.append({
                        'type': 'orphaned_file',
                        'severity': 'medium',
                        'file': file_path,
                        'message': f'File has minimal connections (deps: {dependencies}, dependents: {dependents})'
                    })
        
        return orphaned
    
    def detect_complexity_variance(self) -> List[Dict]:
        """Detect files with dramatically different complexity levels."""
        print("🔍 Analyzing complexity variance...")
        
        complexities = [metrics.get('complexity', 0) for metrics in self.file_metrics.values()]
        if not complexities:
            return []
        
        avg_complexity = sum(complexities) / len(complexities)
        variance_issues = []
        
        for file_path, metrics in self.file_metrics.items():
            complexity = metrics.get('complexity', 0)
            
            # Flag files with >5x average complexity
            if complexity > avg_complexity * 5 and complexity > 10:
                variance_issues.append({
                    'type': 'high_complexity',
                    'severity': 'high',
                    'file': file_path,
                    'complexity': complexity,
                    'average': avg_complexity,
                    'message': f'Complexity {complexity} is {complexity/avg_complexity:.1f}x average'
                })
                self.issues.append(variance_issues[-1])
        
        return variance_issues
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains."""
        print("🔍 Detecting circular dependencies...")
        
        def dfs(node, path, visited):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                return path[cycle_start:]
            
            if node in visited:
                return None
            
            visited.add(node)
            path.append(node)
            
            for dep in self.dependencies.get(node, set()):
                cycle = dfs(dep, path.copy(), visited.copy())
                if cycle:
                    return cycle
            
            return None
        
        cycles = []
        visited_global = set()
        
        for file_path in self.dependencies.keys():
            if file_path not in visited_global:
                cycle = dfs(file_path, [], set())
                if cycle:
                    cycles.append(cycle)
                    self.issues.append({
                        'type': 'circular_dependency',
                        'severity': 'high',
                        'files': cycle,
                        'message': f'Circular dependency detected: {" -> ".join(cycle)}'
                    })
                visited_global.add(file_path)
        
        return cycles
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report."""
        print("📊 Generating integration report...")
        
        # Run all analyses
        orphaned = self.detect_orphaned_files()
        complexity_issues = self.detect_complexity_variance()
        circular_deps = self.detect_circular_dependencies()
        
        # Calculate integration metrics
        total_files = len(self.file_metrics)
        connected_files = len([f for f, deps in self.dependencies.items() if len(deps) > 0])
        connectivity_score = (connected_files / total_files * 100) if total_files > 0 else 0
        
        # Calculate complexity metrics
        complexities = [m.get('complexity', 0) for m in self.file_metrics.values()]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        max_complexity = max(complexities) if complexities else 0
        
        report = {
            'summary': {
                'total_files': total_files,
                'python_files': len(self.python_files),
                'typescript_files': len(self.typescript_files),
                'connectivity_score': round(connectivity_score, 2),
                'average_complexity': round(avg_complexity, 2),
                'max_complexity': max_complexity,
                'total_issues': len(self.issues)
            },
            'issues': {
                'orphaned_files': len(orphaned),
                'complexity_issues': len(complexity_issues),
                'circular_dependencies': len(circular_deps),
                'all_issues': self.issues
            },
            'metrics': {
                'file_metrics': self.file_metrics,
                'dependencies': {k: list(v) for k, v in self.dependencies.items()},
                'reverse_dependencies': {k: list(v) for k, v in self.reverse_dependencies.items()}
            }
        }
        
        return report
    
    def run_analysis(self):
        """Run complete codebase analysis."""
        print("🚀 Starting CityPulse Codebase Integration Analysis")
        print("=" * 50)
        
        self.scan_files()
        self.analyze_python_dependencies()
        self.analyze_typescript_dependencies()
        
        report = self.generate_report()
        
        # Save report
        with open('reports/codebase-integration-analysis.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n📊 ANALYSIS SUMMARY")
        print("=" * 30)
        print(f"Total Files: {report['summary']['total_files']}")
        print(f"Connectivity Score: {report['summary']['connectivity_score']}%")
        print(f"Average Complexity: {report['summary']['average_complexity']}")
        print(f"Total Issues: {report['summary']['total_issues']}")
        print(f"  - Orphaned Files: {report['issues']['orphaned_files']}")
        print(f"  - Complexity Issues: {report['issues']['complexity_issues']}")
        print(f"  - Circular Dependencies: {report['issues']['circular_dependencies']}")
        
        if report['summary']['total_issues'] > 0:
            print(f"\n⚠️  Found {report['summary']['total_issues']} integration issues")
            print("📄 Detailed report saved to: reports/codebase-integration-analysis.json")
        else:
            print("\n✅ No critical integration issues found!")
        
        return report

if __name__ == "__main__":
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    analyzer = CodebaseAnalyzer()
    analyzer.run_analysis()
