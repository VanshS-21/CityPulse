# CityPulse E2E Testing Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will get you up and running with the CityPulse E2E testing framework quickly.

## 📋 Prerequisites

### Required Software

- **Python 3.11+** (Apache Beam compatibility)
- **Node.js 18+** (for frontend testing)
- **Google Cloud SDK** (for GCP services)
- **Git** (for version control)

### GCP Setup

```bash

# Install Google Cloud SDK

curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate

gcloud auth login
gcloud auth application-default login

# Set project (replace with your project ID)

gcloud config set project citypulse-dev
```text
## ⚡ Quick Installation

### 1. Navigate to E2E Tests Directory

```bash
cd e2e-tests/
```text
### 2. Install Python Dependencies

```bash

# Create virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt
```text
### 3. Install Node.js Dependencies

```bash
npm install
```text
### 4. Configure Environment

```bash

# Copy example configuration

cp config/environments.json config/environments.local.json

# Edit configuration for your environment

# Update project IDs, credentials, etc.

```text
## 🧪 Run Your First Tests

### Quick Health Check

```bash

# Validate configuration

npm run validate:config

# Check system health

npm run check:health
```text
### Run API Tests

```bash

# Run all API tests

npm run test:api

# Run specific API tests

npm run test:api -- --filter events
npm run test:api -- --filter users
```text
### Run Data Pipeline Tests

```bash

# Run pipeline tests

npm run test:pipeline

# Run with specific environment

npm run test:pipeline -- --environment development
```text
### Run Complete E2E Suite

```bash

# Full test suite (backend focus)

npm run test:e2e

# Quick smoke tests

npm run test:smoke

# Regression tests

npm run test:regression
```text
## 📊 View Test Results

### Generate Reports

```bash

# Generate comprehensive report

npm run reports:generate

# Serve reports locally

npm run reports:serve

# Open http://localhost:8080 in browser

```text
### Check Coverage

```bash

# Collect coverage data

npm run coverage:collect

# Generate coverage report

npm run coverage:report
```text
## 🛠️ Common Commands

### Development Workflow

```bash

# Run tests during development

npm run test:quick

# Run specific test suite

npm run test:api
npm run test:pipeline
npm run test:performance
npm run test:security

# Run with filters

npm run test:e2e -- --filter "user authentication"
npm run test:e2e -- --include api pipeline
npm run test:e2e -- --exclude performance security
```text
### Maintenance Commands

```bash

# Assess legacy tests

npm run legacy:assess

# Clean up legacy tests

npm run legacy:cleanup

# Clean reports

npm run clean:reports

# Clean test resources

npm run clean:resources
```text
### Environment Management

```bash

# Set up test environment

npm run setup:environment

# Generate test data

npm run setup:test-data

# Monitor performance

npm run monitor:performance
```text
## 🔧 Configuration

### Environment Configuration

Edit `config/environments.json` to match your setup:

```json
{
  "development": {
    "frontend": {
      "baseUrl": "http://localhost:3000"
    },
    "backend": {
      "baseUrl": "http://localhost:8000"
    },
    "gcp": {
      "projectId": "your-project-id",
      "region": "us-central1"
    }
  }
}
```text
### Test Data Configuration

Edit `config/test-data.json` to customize test scenarios:

```json
{
  "events": {
    "validEvent": {
      "title": "Test Event",
      "category": "infrastructure",
      "priority": "medium"
    }
  }
}
```text
## 🐛 Troubleshooting

### Common Issues

#### Authentication Errors

```bash

# Re-authenticate with GCP

gcloud auth application-default login

# Check credentials

gcloud auth list
```text
#### Python Dependencies

```bash

# Upgrade pip

pip install --upgrade pip

# Reinstall dependencies

pip install -r requirements.txt --force-reinstall
```text
#### GCP Permissions

```bash

# Check project permissions

gcloud projects get-iam-policy your-project-id

# Enable required APIs

gcloud services enable pubsub.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable dataflow.googleapis.com
```text
#### Test Failures

```bash

# Run with verbose output

npm run test:e2e -- --verbose

# Run single test for debugging

python -m pytest e2e-tests/core/api-integration/test_events.py::test_create_event -v
```text
### Getting Help

1. **Check Logs**: Test execution logs are in `reports/`
2. **Review Documentation**: See `README.md` and `IMPLEMENTATION_PLAN.md`
3. **Run Health Check**: `npm run check:health`
4. **Validate Config**: `npm run validate:config`

## 📚 Next Steps

### For Developers

1. **Explore API Tests**: Check `core/api-integration/` for examples
2. **Add New Tests**: Follow patterns in existing test files
3. **Customize Data**: Update `config/test-data.json` for your scenarios

### For QA Engineers

1. **Review Test Cases**: Examine test coverage and scenarios
2. **Add Validations**: Enhance test assertions and checks
3. **Create Test Plans**: Use framework for manual test automation

### For DevOps Engineers

1. **CI/CD Integration**: Add tests to deployment pipeline
2. **Environment Setup**: Configure staging/production test environments
3. **Monitoring**: Set up test result monitoring and alerting

## 🎯 Current Focus Areas

Based on the backend-first development approach:

### High Priority

- ✅ **API Testing**: Comprehensive backend API validation
- ✅ **Data Pipeline**: End-to-end data flow testing
- 🚧 **Authentication**: Role-based access control testing

### Medium Priority

- 📋 **Performance**: Load testing and benchmarking
- 📋 **Security**: Vulnerability and security testing
- 📋 **Legacy Cleanup**: Consolidate existing tests

### Future

- 📋 **Frontend**: UI testing when frontend development progresses
- 📋 **Mobile**: Mobile app testing support
- 📋 **Advanced Analytics**: ML/AI testing capabilities

## 💡 Tips for Success

1. **Start Small**: Begin with simple API tests
2. **Use Fixtures**: Leverage test data fixtures for consistency
3. **Clean Up**: Always clean up test resources
4. **Monitor Performance**: Track test execution times
5. **Document Issues**: Report and document any problems found

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: Create GitHub issues for bugs
- **Questions**: Ask in team chat or meetings
- **Contributions**: Follow contribution guidelines

---

#### Happy Testing! 🧪✨

*This framework evolves with your codebase. Keep tests current and relevant.*
