# CityPulse: Urban Issue Reporting & Analytics Platform

CityPulse is a full-stack application for real-time reporting, tracking, and analysis of urban issues. It combines a modern web frontend, a cross-platform mobile app, and a robust Google Cloud backend to provide a comprehensive platform for city management and civic engagement.

## Key Features

-   **Data Ingestion & Processing**: Scalable data pipelines for real-time data ingestion from various sources.
-   **Real-Time Map Dashboard**: Visualize events from Firestore on the web client.
-   **Scalable Data Architecture**: A hybrid data model with Firestore for real-time access and BigQuery for analytics.
-   **AI-Powered Insights (Partially Implemented)**: Sentiment analysis on social media data is implemented; other AI features like event clustering are planned.
-   **Secure API Layer (Planned)**: A robust backend REST API will handle business logic and ensure secure data access.
-   **Multimodal Reporting (Planned)**: Submit issues via web or mobile, including text, images, and video.
-   **Infrastructure as Code (IaC)**: All cloud infrastructure is managed declaratively with Terraform.

## System Architecture

Our architecture is designed for scalability and resilience, leveraging GCP's managed services. For a complete overview, including a detailed data flow diagram and component breakdown, please see our full **[Architecture Document](./ARCHITECTURE.md)**.

## Technology Stack

-   **Frontend (Web)**: Next.js, React, TypeScript, Tailwind CSS
-   **Frontend (Mobile)**: Flutter (planned)
-   **Backend API (Planned)**: Cloud Run / Cloud Functions (Node.js, Python, or Go)
-   **Data Pipelines**: Apache Beam (Python SDK) on Google Cloud Dataflow
-   **Database**: Firestore (real-time), BigQuery (analytical)
-   **Infrastructure**: Terraform on Google Cloud Platform (GCP)
-   **Messaging**: Google Cloud Pub/Sub
-   **AI/ML**: Google Vertex AI (Gemini, Vision API, NLP)

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

## Deployment

-   **Frontend**: The Next.js application can be deployed to Vercel or Firebase Hosting. The deployment is typically triggered by a CI/CD pipeline on a push to the `main` branch.
-   **Backend API**: The API services (Cloud Run/Functions) are deployed via `gcloud` CLI commands, which can also be automated in a CI/CD pipeline.
-   **Data Pipelines**: Dataflow jobs are submitted via the `gcloud` CLI or from a CI/CD environment.

## Troubleshooting

-   **Authentication Errors**: Ensure your `gcloud` SDK is authenticated (`gcloud auth application-default login`) and the correct project is set (`gcloud config set project [PROJECT_ID]`)
-   **Frontend Env Vars**: Make sure your `.env.local` file is correctly configured with the necessary Firebase project details.
-   **Pipeline Failures**: Check the logs for the specific Dataflow job in the Google Cloud Console for detailed error messages. Common issues include permission errors or malformed data in Pub/Sub.

## Documentation

This project is documented in detail across several files:

-   **[Architecture Overview](./ARCHITECTURE.md)**: The complete system design, data flow, and component breakdown.
-   **[Contributing Guide](./CONTRIBUTING.md)**: How to set up your environment, code, and submit contributions.
-   **[Data Access Patterns](./DATA_ACCESS_PATTERNS.md)**: How clients should interact with the backend API and Firestore.
-   **[Code of Conduct](./CODE_OF_CONDUCT.md)**: Our community standards.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
