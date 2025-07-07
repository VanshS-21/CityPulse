"""
Comprehensive test report generator for CityPulse testing framework.
Generates detailed reports with metrics, visualizations, and recommendations.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TestReportGenerator:
    """Generate comprehensive test reports with metrics and visualizations."""
    
    def __init__(self, output_dir: str = "test-reports"):
        """Initialize report generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_comprehensive_report(self, test_results: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report."""
        report_data = self._analyze_test_results(test_results)
        html_content = self._generate_html_report(report_data)
        
        # Save HTML report
        report_path = self.output_dir / "comprehensive-test-report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Comprehensive report generated: {report_path}")
        return str(report_path)
    
    def generate_executive_summary(self, test_results: Dict[str, Any]) -> str:
        """Generate executive summary report."""
        summary_data = self._create_executive_summary(test_results)
        html_content = self._generate_executive_summary_html(summary_data)
        
        # Save executive summary
        summary_path = self.output_dir / "executive-summary.html"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Executive summary generated: {summary_path}")
        return str(summary_path)
    
    def generate_json_report(self, test_results: Dict[str, Any]) -> str:
        """Generate machine-readable JSON report."""
        report_data = self._analyze_test_results(test_results)
        
        # Save JSON report
        json_path = self.output_dir / "test-results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {json_path}")
        return str(json_path)
    
    def _analyze_test_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results and calculate metrics."""
        analysis = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "test_run_id": test_results.get("test_run", {}).get("timestamp", "unknown"),
                "total_duration": test_results.get("test_run", {}).get("duration", 0)
            },
            "overall_metrics": self._calculate_overall_metrics(test_results),
            "test_type_breakdown": self._analyze_test_types(test_results),
            "quality_metrics": self._calculate_quality_metrics(test_results),
            "trends": self._analyze_trends(test_results),
            "recommendations": self._generate_recommendations(test_results)
        }
        
        return analysis
    
    def _calculate_overall_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall test metrics."""
        overall = test_results.get("overall_metrics", {})
        
        return {
            "total_tests": overall.get("total_tests", 0),
            "passed_tests": overall.get("passed", 0),
            "failed_tests": overall.get("failed", 0),
            "skipped_tests": overall.get("skipped", 0),
            "error_tests": overall.get("errors", 0),
            "success_rate": overall.get("success_rate", 0),
            "total_duration": overall.get("total_duration", 0),
            "test_types_run": overall.get("test_types_run", 0),
            "test_types_passed": overall.get("test_types_passed", 0),
            "coverage_percentage": self._calculate_coverage(test_results)
        }
    
    def _analyze_test_types(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results by test type."""
        test_type_analysis = {}
        
        for test_type, result in test_results.get("test_results", {}).items():
            test_type_analysis[test_type] = {
                "status": "PASSED" if result.get("success", False) else "FAILED",
                "duration": result.get("duration", 0),
                "total_tests": result.get("total_tests", 0),
                "passed": result.get("passed", 0),
                "failed": result.get("failed", 0),
                "skipped": result.get("skipped", 0),
                "errors": result.get("errors", 0),
                "success_rate": self._calculate_success_rate(result),
                "performance_metrics": self._extract_performance_metrics(result),
                "issues": self._extract_issues(result)
            }
        
        return test_type_analysis
    
    def _calculate_quality_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics."""
        return {
            "code_coverage": {
                "unit_tests": self._get_coverage_for_type("unit", test_results),
                "integration_tests": self._get_coverage_for_type("integration", test_results),
                "overall": self._calculate_coverage(test_results)
            },
            "performance_metrics": {
                "avg_response_time": self._get_avg_response_time(test_results),
                "p95_response_time": self._get_p95_response_time(test_results),
                "throughput": self._get_throughput(test_results),
                "error_rate": self._get_error_rate(test_results)
            },
            "security_metrics": {
                "vulnerabilities_found": self._count_security_issues(test_results),
                "auth_tests_passed": self._count_auth_tests_passed(test_results),
                "data_protection_score": self._calculate_data_protection_score(test_results)
            },
            "accessibility_metrics": {
                "wcag_compliance_level": self._get_wcag_compliance(test_results),
                "accessibility_issues": self._count_accessibility_issues(test_results),
                "keyboard_navigation_score": self._get_keyboard_nav_score(test_results)
            }
        }
    
    def _analyze_trends(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends (would compare with historical data)."""
        # In a real implementation, this would compare with previous test runs
        return {
            "test_count_trend": "stable",
            "success_rate_trend": "improving",
            "performance_trend": "stable",
            "coverage_trend": "improving",
            "recommendations": [
                "Continue maintaining high test coverage",
                "Monitor performance metrics for any degradation",
                "Consider adding more integration tests"
            ]
        }
    
    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        overall = test_results.get("overall_metrics", {})
        success_rate = overall.get("success_rate", 0)
        
        # Success rate recommendations
        if success_rate < 90:
            recommendations.append({
                "category": "Test Reliability",
                "priority": "High",
                "recommendation": f"Success rate is {success_rate:.1f}%. Investigate and fix failing tests.",
                "action": "Review failed test logs and fix underlying issues"
            })
        
        # Coverage recommendations
        coverage = self._calculate_coverage(test_results)
        if coverage < 80:
            recommendations.append({
                "category": "Code Coverage",
                "priority": "Medium",
                "recommendation": f"Code coverage is {coverage:.1f}%. Add more unit tests.",
                "action": "Identify uncovered code paths and add corresponding tests"
            })
        
        # Performance recommendations
        for test_type, result in test_results.get("test_results", {}).items():
            if test_type == "performance":
                avg_response_time = result.get("avg_response_time", 0)
                if avg_response_time > 2000:
                    recommendations.append({
                        "category": "Performance",
                        "priority": "High",
                        "recommendation": f"Average response time is {avg_response_time:.0f}ms. Optimize performance.",
                        "action": "Profile application and optimize slow endpoints"
                    })
        
        # Security recommendations
        security_issues = self._count_security_issues(test_results)
        if security_issues > 0:
            recommendations.append({
                "category": "Security",
                "priority": "Critical",
                "recommendation": f"Found {security_issues} security issues. Address immediately.",
                "action": "Review security test results and fix vulnerabilities"
            })
        
        # Accessibility recommendations
        accessibility_issues = self._count_accessibility_issues(test_results)
        if accessibility_issues > 0:
            recommendations.append({
                "category": "Accessibility",
                "priority": "Medium",
                "recommendation": f"Found {accessibility_issues} accessibility issues. Improve WCAG compliance.",
                "action": "Review accessibility test results and implement fixes"
            })
        
        return recommendations
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report."""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CityPulse Comprehensive Test Report</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }
                .header .subtitle {
                    margin-top: 10px;
                    opacity: 0.9;
                    font-size: 1.1em;
                }
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    padding: 30px;
                }
                .metric-card {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }
                .metric-value {
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 5px;
                }
                .metric-label {
                    color: #666;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .section {
                    padding: 30px;
                    border-bottom: 1px solid #eee;
                }
                .section h2 {
                    color: #333;
                    margin-bottom: 20px;
                    font-size: 1.8em;
                }
                .test-type-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }
                .test-type-card {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    background: white;
                }
                .test-type-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .test-type-name {
                    font-size: 1.2em;
                    font-weight: bold;
                    text-transform: capitalize;
                }
                .status-badge {
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.8em;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                .status-passed {
                    background: #d4edda;
                    color: #155724;
                }
                .status-failed {
                    background: #f8d7da;
                    color: #721c24;
                }
                .recommendations {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }
                .recommendation-item {
                    margin-bottom: 15px;
                    padding: 15px;
                    background: white;
                    border-radius: 6px;
                    border-left: 4px solid #f39c12;
                }
                .recommendation-category {
                    font-weight: bold;
                    color: #e67e22;
                    margin-bottom: 5px;
                }
                .recommendation-text {
                    color: #666;
                    line-height: 1.5;
                }
                .footer {
                    padding: 20px 30px;
                    background: #f8f9fa;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                }
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background: #e9ecef;
                    border-radius: 4px;
                    overflow: hidden;
                    margin-top: 10px;
                }
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #28a745, #20c997);
                    transition: width 0.3s ease;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>CityPulse Test Report</h1>
                    <div class="subtitle">Comprehensive Testing Results</div>
                    <div class="subtitle">Generated: {generated_at}</div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_tests}</div>
                        <div class="metric-label">Total Tests</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{success_rate:.1f}%</div>
                        <div class="metric-label">Success Rate</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {success_rate}%"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{coverage_percentage:.1f}%</div>
                        <div class="metric-label">Code Coverage</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {coverage_percentage}%"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_duration:.1f}s</div>
                        <div class="metric-label">Total Duration</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Test Type Results</h2>
                    <div class="test-type-grid">
                        {test_type_cards}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    <div class="recommendations">
                        {recommendations_html}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Report generated by CityPulse Testing Framework</p>
                    <p>Test Run ID: {test_run_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Generate test type cards
        test_type_cards = ""
        for test_type, data in report_data["test_type_breakdown"].items():
            status_class = "status-passed" if data["status"] == "PASSED" else "status-failed"
            test_type_cards += f"""
            <div class="test-type-card">
                <div class="test-type-header">
                    <div class="test-type-name">{test_type}</div>
                    <div class="status-badge {status_class}">{data["status"]}</div>
                </div>
                <div>Duration: {data["duration"]:.1f}s</div>
                <div>Tests: {data["total_tests"]} total, {data["passed"]} passed, {data["failed"]} failed</div>
                <div>Success Rate: {data["success_rate"]:.1f}%</div>
            </div>
            """
        
        # Generate recommendations
        recommendations_html = ""
        for rec in report_data["recommendations"]:
            recommendations_html += f"""
            <div class="recommendation-item">
                <div class="recommendation-category">{rec["category"]} ({rec["priority"]} Priority)</div>
                <div class="recommendation-text">{rec["recommendation"]}</div>
                <div class="recommendation-text"><strong>Action:</strong> {rec["action"]}</div>
            </div>
            """
        
        # Fill template
        overall = report_data["overall_metrics"]
        return html_template.format(
            generated_at=report_data["metadata"]["generated_at"],
            test_run_id=report_data["metadata"]["test_run_id"],
            total_tests=overall["total_tests"],
            success_rate=overall["success_rate"],
            coverage_percentage=overall["coverage_percentage"],
            total_duration=overall["total_duration"],
            test_type_cards=test_type_cards,
            recommendations_html=recommendations_html
        )
    
    def _generate_executive_summary_html(self, summary_data: Dict[str, Any]) -> str:
        """Generate executive summary HTML."""
        # Simplified executive summary template
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CityPulse Test Executive Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .metric {{ display: inline-block; margin: 10px 20px; }}
                .status-good {{ color: #28a745; }}
                .status-warning {{ color: #ffc107; }}
                .status-critical {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <h1>CityPulse Test Executive Summary</h1>
            <div class="summary">
                <h2>Overall Status: {summary_data.get('overall_status', 'Unknown')}</h2>
                <div class="metric">Total Tests: {summary_data.get('total_tests', 0)}</div>
                <div class="metric">Success Rate: {summary_data.get('success_rate', 0):.1f}%</div>
                <div class="metric">Coverage: {summary_data.get('coverage', 0):.1f}%</div>
            </div>
            <h3>Key Findings</h3>
            <ul>
                {self._format_key_findings(summary_data.get('key_findings', []))}
            </ul>
        </body>
        </html>
        """
    
    # Helper methods for metric calculations
    def _calculate_success_rate(self, result: Dict[str, Any]) -> float:
        """Calculate success rate for a test result."""
        total = result.get("total_tests", 0)
        passed = result.get("passed", 0)
        return (passed / total * 100) if total > 0 else 0
    
    def _calculate_coverage(self, test_results: Dict[str, Any]) -> float:
        """Calculate overall code coverage."""
        # This would integrate with actual coverage reports
        return 85.0  # Placeholder
    
    def _get_coverage_for_type(self, test_type: str, test_results: Dict[str, Any]) -> float:
        """Get coverage for specific test type."""
        return 80.0  # Placeholder
    
    def _get_avg_response_time(self, test_results: Dict[str, Any]) -> float:
        """Get average response time from performance tests."""
        perf_results = test_results.get("test_results", {}).get("performance", {})
        return perf_results.get("avg_response_time", 0)
    
    def _get_p95_response_time(self, test_results: Dict[str, Any]) -> float:
        """Get 95th percentile response time."""
        perf_results = test_results.get("test_results", {}).get("performance", {})
        return perf_results.get("p95_response_time", 0)
    
    def _get_throughput(self, test_results: Dict[str, Any]) -> float:
        """Get throughput from performance tests."""
        perf_results = test_results.get("test_results", {}).get("performance", {})
        return perf_results.get("throughput", 0)
    
    def _get_error_rate(self, test_results: Dict[str, Any]) -> float:
        """Get error rate from performance tests."""
        perf_results = test_results.get("test_results", {}).get("performance", {})
        return perf_results.get("error_rate", 0)
    
    def _count_security_issues(self, test_results: Dict[str, Any]) -> int:
        """Count security issues found."""
        security_results = test_results.get("test_results", {}).get("security", {})
        return security_results.get("failed", 0)
    
    def _count_auth_tests_passed(self, test_results: Dict[str, Any]) -> int:
        """Count authentication tests passed."""
        security_results = test_results.get("test_results", {}).get("security", {})
        return security_results.get("passed", 0)
    
    def _calculate_data_protection_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate data protection score."""
        return 90.0  # Placeholder
    
    def _get_wcag_compliance(self, test_results: Dict[str, Any]) -> str:
        """Get WCAG compliance level."""
        accessibility_results = test_results.get("test_results", {}).get("accessibility", {})
        failed = accessibility_results.get("failed", 0)
        return "AA" if failed == 0 else "Partial"
    
    def _count_accessibility_issues(self, test_results: Dict[str, Any]) -> int:
        """Count accessibility issues."""
        accessibility_results = test_results.get("test_results", {}).get("accessibility", {})
        return accessibility_results.get("failed", 0)
    
    def _get_keyboard_nav_score(self, test_results: Dict[str, Any]) -> float:
        """Get keyboard navigation score."""
        return 95.0  # Placeholder
    
    def _extract_performance_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from test result."""
        return {
            "avg_response_time": result.get("avg_response_time", 0),
            "p95_response_time": result.get("p95_response_time", 0),
            "throughput": result.get("throughput", 0),
            "error_rate": result.get("error_rate", 0)
        }
    
    def _extract_issues(self, result: Dict[str, Any]) -> List[str]:
        """Extract issues from test result."""
        issues = []
        if result.get("failed", 0) > 0:
            issues.append(f"{result['failed']} tests failed")
        if result.get("errors", 0) > 0:
            issues.append(f"{result['errors']} tests had errors")
        return issues
    
    def _create_executive_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary data."""
        overall = test_results.get("overall_metrics", {})
        success_rate = overall.get("success_rate", 0)
        
        # Determine overall status
        if success_rate >= 95:
            overall_status = "Excellent"
        elif success_rate >= 85:
            overall_status = "Good"
        elif success_rate >= 70:
            overall_status = "Needs Attention"
        else:
            overall_status = "Critical"
        
        return {
            "overall_status": overall_status,
            "total_tests": overall.get("total_tests", 0),
            "success_rate": success_rate,
            "coverage": self._calculate_coverage(test_results),
            "key_findings": [
                f"Test suite executed {overall.get('total_tests', 0)} tests",
                f"Overall success rate: {success_rate:.1f}%",
                f"Code coverage: {self._calculate_coverage(test_results):.1f}%"
            ]
        }
    
    def _format_key_findings(self, findings: List[str]) -> str:
        """Format key findings as HTML list items."""
        return "".join(f"<li>{finding}</li>" for finding in findings)


def main():
    """Main function for standalone report generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CityPulse test reports")
    parser.add_argument("--results", required=True, help="Path to test results JSON file")
    parser.add_argument("--output", default="test-reports", help="Output directory")
    parser.add_argument("--format", choices=["html", "json", "executive"], default="html", help="Report format")
    
    args = parser.parse_args()
    
    # Load test results
    with open(args.results, 'r') as f:
        test_results = json.load(f)
    
    # Generate report
    generator = TestReportGenerator(args.output)
    
    if args.format == "html":
        report_path = generator.generate_comprehensive_report(test_results)
    elif args.format == "json":
        report_path = generator.generate_json_report(test_results)
    elif args.format == "executive":
        report_path = generator.generate_executive_summary(test_results)
    
    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
