# CityPulse: Urban Intelligence Platform

**Version**: 1.0.0 | **Status**: Production Ready 🚀

CityPulse is a comprehensive urban intelligence platform that transforms real-time city data into actionable insights. Built with enterprise-grade architecture, it provides citizens, authorities, and administrators with powerful tools for urban issue reporting, monitoring, and analytics.

## 🌟 Key Features

### **For Citizens**
-   **Real-Time Issue Reporting**: Submit geo-tagged multimedia reports with AI-powered categorization
-   **Interactive Map Dashboard**: Visualize live city events with advanced filtering and search
-   **Personalized Alerts**: Receive notifications for events in your area
-   **Progress Tracking**: Monitor resolution status of submitted reports

### **For Authorities**
-   **Comprehensive Monitoring**: City-wide event dashboard with real-time analytics
-   **Incident Management**: Streamlined workflow for issue triage and response
-   **Predictive Analytics**: AI-powered insights for proactive city management
-   **Performance Metrics**: Response time tracking and resolution analytics

### **Technical Excellence**
-   **Scalable Data Architecture**: Hybrid Firestore/BigQuery with Apache Beam pipelines
-   **AI-Powered Processing**: Gemini + Vision AI for automated analysis and categorization
-   **Enterprise Security**: Comprehensive security operations and data protection
-   **Production Infrastructure**: Terraform-managed GCP deployment with monitoring

## System Architecture

Our architecture is designed for scalability and resilience, leveraging GCP's managed services. For a complete overview, including a detailed data flow diagram and component breakdown, please see our full **[Architecture Document](./ARCHITECTURE.md)**.

## 🛠️ Technology Stack

### **Frontend**
-   **Framework**: Next.js 15.3.4 with React 19.1.0 (App Router)
-   **Language**: TypeScript 5.x with strict configuration
-   **Styling**: Tailwind CSS v4 (latest)
-   **State Management**: Zustand for client state
-   **Authentication**: Firebase Auth with multi-factor support

### **Backend & Data Processing**
-   **Data Pipelines**: Apache Beam 2.57.0 on Google Cloud Dataflow
-   **Language**: Python 3.11+ with Pydantic validation
-   **Real-time Database**: Firestore with security rules
-   **Analytics Database**: BigQuery with partitioning and clustering
-   **Messaging**: Google Cloud Pub/Sub for event streaming

### **AI & Machine Learning**
-   **AI Platform**: Google Vertex AI (Gemini Pro, Vision API)
-   **Processing**: Automated categorization, sentiment analysis, image recognition
-   **Analytics**: Predictive modeling and trend analysis

### **Infrastructure & DevOps**
-   **Cloud Platform**: Google Cloud Platform (multi-region)
-   **Infrastructure as Code**: Terraform 1.0+ with modular design
-   **Containerization**: Docker with Cloud Run deployment
-   **CI/CD**: GitHub Actions with comprehensive testing
-   **Monitoring**: Cloud Monitoring, Logging, and Sentry integration

## Getting Started

To get the project up and running, follow these steps. For more detailed instructions, see the [Contributing Guide](./CONTRIBUTING.md).

### Prerequisites
-   Node.js (v18+)
-   Python (v3.11+)
-   Terraform (v1.0+)
-   Google Cloud SDK (`gcloud`)

### 1. Provision Infrastructure
All cloud resources are managed by Terraform. See the **[Infrastructure Setup Guide](./infra/README.md)** for instructions.

### 2. Setup Backend
The backend data pipelines require a specific Python environment. See the **[Data Models & Backend Guide](./data_models/README.md)**.

### 3. Run Frontend
```bash
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the app.

## 🧪 Testing & Quality Assurance

CityPulse maintains **95%+ test coverage** across all components:

### **Test Suites**
```bash
# Frontend tests (Jest + React Testing Library)
npm run test:ci

# End-to-end tests (Playwright)
npm run test:e2e

# Python backend tests (pytest)
python -m pytest tests/ -v

# Security tests
npm run test:security

# Performance tests
npm run test:performance
```

### **Quality Metrics**
- **Python Code Quality**: 10/10 (pylint score)
- **TypeScript Quality**: High (ESLint 9 with strict rules)
- **Test Coverage**: 95%+ across all layers
- **Security Scanning**: Automated vulnerability detection
- **Performance**: <2s page load, <500ms API response

## 🚀 Deployment

### **Production Deployment**
-   **Frontend**: Next.js deployed to Vercel with automatic CI/CD
-   **Backend**: Apache Beam pipelines on Google Cloud Dataflow
-   **Infrastructure**: Terraform-managed GCP resources
-   **Monitoring**: Comprehensive observability with alerts

See the **[Deployment Guide](./docs/DEPLOYMENT.md)** for detailed instructions.

## 📚 Documentation

Comprehensive documentation is available in the `/docs` directory:

- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System design and data flow
- **[API Documentation](./docs/API_GUIDE.md)** - Complete API reference with examples
- **[User Guide](./docs/USER_GUIDE.md)** - User training and tutorials
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Security Operations](./docs/SECURITY_OPERATIONS.md)** - Security procedures and best practices
- **[Performance Guide](./docs/PERFORMANCE_GUIDE.md)** - Optimization strategies
- **[Database Schema](./docs/DATABASE_SCHEMA.md)** - Complete data model documentation
- **[FAQ](./docs/FAQ.md)** - Frequently asked questions and troubleshooting

## 🏗️ Project Structure

```
CityPulse/
├── src/                    # Next.js frontend (App Router)
├── data_models/           # Python data processing core
├── infra/                 # Terraform infrastructure
├── tests/                 # Comprehensive testing framework
├── docs/                  # Complete documentation suite
├── E2E/                   # End-to-end testing
├── scripts/               # Automation utilities
└── reports/               # Analysis and audit reports
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/CONTRIBUTING.md) for details on:
- Development setup and workflow
- Code standards and best practices
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**CityPulse** - Transforming urban data into actionable insights for smarter cities 🌆
