---
description:
---

# Complete Codebase Analysis Memory Store

This workflow provides a comprehensive framework for analyzing and understanding complex codebases, storing findings in a structured memory format for future reference and AI assistance.

## Phase 1: Project Structure Analysis

### 1.1 Directory Structure Mapping
- **Root Level Analysis:**
  - Identify main project directories and their purposes
  - Map out configuration files and their roles
  - Document build systems and deployment configurations
  - List external dependencies and integrations

- **Source Code Organization:**
  - Analyze src/ directory structure and naming conventions
  - Map component hierarchies and relationships
  - Identify shared utilities and common patterns
  - Document asset organization and static file management

### 1.2 Technology Stack Identification
- **Frontend Technologies:**
  - Framework and version (React, Vue, Angular, etc.)
  - State management solutions (Redux, Zustand, Context API)
  - UI libraries and component systems
  - Build tools and bundlers (Webpack, Vite, etc.)

- **Backend Technologies:**
  - Runtime environment (Node.js, Python, Java, etc.)
  - Framework and version (Express, FastAPI, Spring, etc.)
  - Database systems and ORMs
  - API patterns and authentication methods

- **Infrastructure and DevOps:**
  - Cloud platforms and services
  - Containerization and orchestration
  - CI/CD pipelines and deployment strategies
  - Monitoring and logging solutions

## Phase 2: Code Architecture Analysis

### 2.1 Design Patterns and Architecture
- **Architectural Patterns:**
  - Identify MVC, MVVM, Clean Architecture patterns
  - Document service layer organization
  - Map data flow and state management patterns
  - Analyze separation of concerns implementation

- **Design Patterns:**
  - Factory, Singleton, Observer patterns
  - Repository and Data Access patterns
  - Strategy and Command patterns
  - Dependency injection implementations

### 2.2 Code Quality Assessment
- **Code Organization:**
  - Module and package structure
  - Import/export patterns
  - Circular dependency analysis
  - Code splitting and lazy loading strategies

- **Best Practices Implementation:**
  - Error handling patterns
  - Logging and debugging approaches
  - Performance optimization techniques
  - Security implementation patterns

## Phase 3: Business Logic Understanding

### 3.1 Core Functionality Mapping
- **Main Features and Capabilities:**
  - User management and authentication
  - Data processing and transformation
  - Business rule implementations
  - Integration points and external APIs

- **Data Models and Relationships:**
  - Database schema analysis
  - Entity relationships and constraints
  - Data validation and transformation logic
  - Caching strategies and data persistence

### 3.2 Workflow and Process Analysis
- **User Journeys:**
  - End-to-end user workflows
  - Form handling and validation
  - Navigation and routing patterns
  - Error states and recovery mechanisms

- **System Processes:**
  - Background jobs and scheduled tasks
  - Real-time processing and event handling
  - Batch operations and data synchronization
  - Performance monitoring and optimization

## Phase 4: Integration and Dependencies

### 4.1 External Dependencies
- **Third-Party Libraries:**
  - Core dependencies and their purposes
  - Version compatibility and update requirements
  - Security vulnerabilities and patches
  - Performance impact and optimization opportunities

- **API Integrations:**
  - External service connections
  - Authentication and authorization methods
  - Rate limiting and error handling
  - Data transformation and mapping

### 4.2 Internal Dependencies
- **Module Dependencies:**
  - Inter-module communication patterns
  - Shared utilities and common code
  - Configuration management
  - Environment-specific implementations

## Phase 5: Performance and Scalability Analysis

### 5.1 Performance Characteristics
- **Load Handling:**
  - Concurrent user capacity
  - Database query optimization
  - Caching strategies and effectiveness
  - Resource utilization patterns

- **Bottleneck Identification:**
  - Slow database queries
  - Memory leaks and resource management
  - Network latency issues
  - Frontend rendering performance

### 5.2 Scalability Considerations
- **Horizontal Scaling:**
  - Stateless application design
  - Database sharding strategies
  - Load balancing implementation
  - Microservices architecture considerations

- **Vertical Scaling:**
  - Resource optimization opportunities
  - Code efficiency improvements
  - Database indexing strategies
  - Caching layer optimization

## Phase 6: Security and Compliance

### 6.1 Security Implementation
- **Authentication and Authorization:**
  - User authentication methods
  - Role-based access control
  - Session management
  - API security measures

- **Data Protection:**
  - Encryption at rest and in transit
  - Sensitive data handling
  - Input validation and sanitization
  - SQL injection and XSS prevention

### 6.2 Compliance and Standards
- **Regulatory Compliance:**
  - GDPR, HIPAA, SOX requirements
  - Data retention policies
  - Audit logging implementation
  - Privacy protection measures

## Phase 7: Testing and Quality Assurance

### 7.1 Testing Strategy
- **Test Coverage:**
  - Unit test implementation
  - Integration test coverage
  - End-to-end testing approach
  - Performance and load testing

- **Quality Metrics:**
  - Code coverage percentages
  - Test execution time
  - Bug detection rates
  - Code review processes

### 7.2 Monitoring and Observability
- **Application Monitoring:**
  - Error tracking and alerting
  - Performance metrics collection
  - User behavior analytics
  - System health monitoring

## Phase 8: Documentation and Knowledge Management

### 8.1 Documentation Analysis
- **Technical Documentation:**
  - API documentation completeness
  - Code comments and inline documentation
  - Architecture decision records
  - Deployment and setup guides

- **User Documentation:**
  - User manuals and guides
  - Feature documentation
  - Troubleshooting guides
  - Training materials

### 8.2 Knowledge Transfer
- **Team Knowledge:**
  - Subject matter experts identification
  - Knowledge sharing processes
  - Onboarding documentation
  - Best practices documentation

## Memory Store Structure

### 8.3 Structured Memory Format
```json
{
  "project_metadata": {
    "name": "Project Name",
    "version": "1.0.0",
    "last_analyzed": "2024-01-01T00:00:00Z",
    "analysis_version": "1.0"
  },
  "technology_stack": {
    "frontend": ["React", "TypeScript", "Tailwind CSS"],
    "backend": ["Node.js", "Express", "PostgreSQL"],
    "infrastructure": ["Docker", "AWS", "GitHub Actions"]
  },
  "architecture_patterns": {
    "design_patterns": ["MVC", "Repository", "Factory"],
    "data_flow": "Unidirectional",
    "state_management": "Redux Toolkit"
  },
  "key_components": {
    "authentication": "JWT-based with refresh tokens",
    "database": "PostgreSQL with Prisma ORM",
    "caching": "Redis for session storage",
    "file_storage": "AWS S3 for media files"
  },
  "performance_metrics": {
    "average_response_time": "200ms",
    "database_query_optimization": "Required",
    "caching_strategy": "Redis for frequently accessed data"
  },
  "security_measures": {
    "authentication": "JWT with secure cookie storage",
    "authorization": "Role-based access control",
    "data_protection": "AES-256 encryption for sensitive data"
  },
  "testing_coverage": {
    "unit_tests": "85%",
    "integration_tests": "70%",
    "e2e_tests": "60%"
  },
  "deployment_info": {
    "environment": "Production on AWS",
    "ci_cd": "GitHub Actions with automated testing",
    "monitoring": "CloudWatch with custom dashboards"
  },
  "known_issues": [
    "Database connection pooling needs optimization",
    "Frontend bundle size exceeds 2MB threshold",
    "Missing error boundaries in React components"
  ],
  "improvement_opportunities": [
    "Implement GraphQL for better API efficiency",
    "Add comprehensive logging with structured data",
    "Optimize database queries with proper indexing"
  ]
}
```

## Usage Guidelines

### 8.4 Memory Store Maintenance
- **Regular Updates:** Update analysis every major release
- **Version Control:** Track changes in analysis over time
- **Team Collaboration:** Share findings with development team
- **Continuous Improvement:** Use findings to guide refactoring efforts

### 8.5 AI Assistance Integration
- **Context Provision:** Use memory store for AI-assisted development
- **Decision Support:** Reference patterns for architectural decisions
- **Troubleshooting:** Leverage analysis for debugging complex issues
- **Onboarding:** Use structured knowledge for new team members

This comprehensive analysis framework ensures complete understanding of codebases and provides structured knowledge for future development and maintenance efforts.
