# CityPulse Comprehensive Testing Framework

This directory contains the complete testing framework for CityPulse, providing comprehensive coverage across all application layers and quality aspects.

## 📁 Test Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_data_pipelines.py      # Data pipeline component tests
│   ├── test_frontend_components.py # React component tests
│   └── test_services.py            # Service layer tests
├── integration/                    # Integration tests for component interactions
│   ├── test_api_endpoints.py       # API endpoint integration tests
│   ├── test_database_operations.py # Database integration tests
│   └── test_external_services.py   # External service integration tests
├── e2e/                            # End-to-end tests for complete workflows
│   └── test_user_workflows.py      # Complete user journey tests
├── performance/                    # Performance and load testing
│   ├── test_load_testing.py        # Load testing and scalability
│   └── test_bottleneck_analysis.py # Performance bottleneck identification
├── security/                      # Security testing
│   ├── test_authentication_security.py # Auth and authorization tests
│   └── test_vulnerability_scanning.py  # Vulnerability and data protection tests
├── accessibility/                 # Accessibility testing
│   ├── test_wcag_compliance.py     # WCAG compliance tests
│   └── test_screen_reader_compatibility.py # Screen reader and keyboard tests
├── conftest.py                    # Shared test configuration and fixtures
├── test_runner.py                 # Comprehensive test runner
└── README.md                      # This documentation
```

## 🧪 Test Types

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Coverage**: Data models, services, utilities, React components
- **Tools**: pytest, Jest, React Testing Library
- **Run Time**: < 5 minutes
- **Coverage Target**: 90%+

### Integration Tests
- **Purpose**: Test component interactions and data flow
- **Coverage**: API endpoints, database operations, external services
- **Tools**: pytest, TestClient, mock services
- **Run Time**: 10-15 minutes
- **Coverage Target**: 80%+

### End-to-End Tests
- **Purpose**: Test complete user workflows
- **Coverage**: User journeys, cross-component functionality
- **Tools**: Playwright, browser automation
- **Run Time**: 20-30 minutes
- **Coverage Target**: Critical user paths

### Performance Tests
- **Purpose**: Validate system performance under load
- **Coverage**: Response times, throughput, scalability
- **Tools**: Custom load testing framework, psutil
- **Run Time**: 30-60 minutes
- **Thresholds**: Response time < 2s (95th percentile), Error rate < 5%

### Security Tests
- **Purpose**: Identify security vulnerabilities
- **Coverage**: Authentication, authorization, input validation
- **Tools**: Custom security testing framework
- **Run Time**: 15-30 minutes
- **Standards**: OWASP Top 10, secure coding practices

### Accessibility Tests
- **Purpose**: Ensure WCAG compliance and usability
- **Coverage**: Screen readers, keyboard navigation, color contrast
- **Tools**: Playwright, axe-core simulation
- **Run Time**: 10-20 minutes
- **Standards**: WCAG 2.1 AA compliance

## 🚀 Quick Start

### Prerequisites
```bash
# Python dependencies
pip install pytest pytest-asyncio pytest-cov playwright psutil bcrypt cryptography

# Install Playwright browsers
playwright install

# Node.js dependencies (for frontend tests)
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

### Running Tests

#### Run All Tests
```bash
python tests/test_runner.py
```

#### Run Specific Test Types
```bash
# Unit tests only
python tests/test_runner.py --types unit

# Integration and E2E tests
python tests/test_runner.py --types integration e2e

# Performance tests
python tests/test_runner.py --types performance

# Security tests
python tests/test_runner.py --types security

# Accessibility tests
python tests/test_runner.py --types accessibility
```

#### Run with pytest directly
```bash
# Unit tests
pytest tests/unit/ -v --cov=data_models --cov=src

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v --headed  # Run with visible browser

# Performance tests
pytest tests/performance/ -v -m performance

# Security tests
pytest tests/security/ -v -m security

# Accessibility tests
pytest tests/accessibility/ -v -m accessibility
```

## 📊 Test Reports

Test reports are generated in the `test-reports/` directory:

- `comprehensive-report.html` - Overall test summary
- `comprehensive-report.json` - Machine-readable results
- `{test-type}-coverage/` - Coverage reports by test type
- `{test-type}-junit.xml` - JUnit XML for CI/CD integration
- `bottleneck-analysis.json` - Performance bottleneck analysis

## 🔧 Configuration

### Test Configuration
Edit `conftest.py` to modify:
- Test environment settings
- Mock service configurations
- Performance thresholds
- Security test parameters
- Accessibility standards

### Custom Test Runner Configuration
Create `test-config.json`:
```json
{
  "test_types": {
    "unit": {
      "enabled": true,
      "timeout": 300,
      "parallel": true,
      "coverage": true
    },
    "performance": {
      "enabled": false,
      "timeout": 3600,
      "parallel": false
    }
  },
  "reporting": {
    "formats": ["json", "html", "junit"],
    "coverage_threshold": 80
  }
}
```

## 🎯 Test Markers

Use pytest markers to run specific test categories:

```bash
# Run only smoke tests
pytest -m smoke

# Run slow tests
pytest -m slow

# Run security tests
pytest -m security

# Run accessibility tests
pytest -m accessibility

# Run performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

## 📈 Coverage Requirements

| Test Type | Minimum Coverage | Target Coverage |
|-----------|------------------|-----------------|
| Unit Tests | 80% | 90%+ |
| Integration Tests | 70% | 80%+ |
| E2E Tests | N/A | Critical paths |
| Performance Tests | N/A | Key endpoints |
| Security Tests | N/A | All auth flows |
| Accessibility Tests | N/A | All UI components |

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Comprehensive Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          playwright install
      
      - name: Run comprehensive tests
        run: python tests/test_runner.py --types unit integration
      
      - name: Upload test reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: test-reports/
```

## 🐛 Debugging Tests

### Common Issues and Solutions

1. **Browser tests failing**
   ```bash
   # Install browsers
   playwright install
   
   # Run with visible browser for debugging
   pytest tests/e2e/ --headed --slowmo=1000
   ```

2. **Performance tests timing out**
   ```bash
   # Increase timeout
   pytest tests/performance/ --timeout=3600
   ```

3. **Coverage reports missing**
   ```bash
   # Ensure coverage packages installed
   pip install pytest-cov coverage
   ```

### Debug Mode
```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debugging
pytest tests/unit/test_services.py::TestFirestoreService::test_document_crud -v -s
```

## 📝 Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names: `test_user_can_submit_report_successfully`

### Test Structure
```python
class TestFeatureName:
    """Test cases for specific feature."""
    
    def setup_method(self):
        """Setup for each test method."""
        pass
    
    @pytest.mark.unit
    def test_specific_functionality(self):
        """Test specific functionality with clear description."""
        # Arrange
        # Act
        # Assert
        pass
```

### Fixtures and Utilities
- Use fixtures in `conftest.py` for shared setup
- Create utility functions for common test operations
- Mock external dependencies appropriately

## 🔍 Test Quality Guidelines

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Clear Assertions**: Use descriptive assertion messages
3. **Proper Mocking**: Mock external dependencies, not internal logic
4. **Test Data**: Use realistic but safe test data
5. **Error Cases**: Test both success and failure scenarios
6. **Performance**: Keep unit tests fast (< 1s each)

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/python/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Add appropriate markers and documentation
3. Update this README if adding new test types or significant changes
4. Ensure tests pass in CI/CD pipeline
5. Maintain or improve overall test coverage

## 📞 Support

For questions about the testing framework:
- Check existing test examples in each directory
- Review the `conftest.py` for available fixtures
- Consult the test runner documentation in `test_runner.py`
- Create an issue for framework improvements or bugs
