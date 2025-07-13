# CityPulse Architecture Overview

This document provides a detailed overview of the CityPulse application architecture. It reflects both the current implementation and planned features as outlined in the project's task list, ensuring a comprehensive understanding of the system's evolution.

## 📚 Related Documentation

- **[Database Schema](./DATABASE_SCHEMA.md)** - Detailed database design and relationships
- **[API Guide](./API_GUIDE.md)** - Complete API reference and examples
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment procedures
- **[Security Operations](./SECURITY_OPERATIONS.md)** - Security architecture and procedures
- **[Performance Guide](./PERFORMANCE_GUIDE.md)** - Performance optimization strategies
- **[Tech Stack Reference](./TECH_STACK_REFERENCE.md)** - Technology stack details

## 1. High-Level Design

CityPulse is a comprehensive platform for urban issue reporting and analytics, built on a modular, scalable, and resilient architecture. It leverages serverless and managed services from Google Cloud Platform (GCP) to deliver a robust solution.

The architecture includes:

-   **Client Applications**: A responsive web frontend and a cross-platform mobile app for citizen and authority interaction.
-   **Backend Services**: A secure REST API layer for business logic and a suite of asynchronous data processing pipelines.
-   **AI/ML Integration**: A sophisticated intelligence layer for processing multimodal data (text, images) to generate actionable insights.
-   **Data Layer**: A hybrid data storage solution using Firestore for real-time data and BigQuery for analytics and historical data.
-   **Infrastructure as Code (IaC)**: All cloud resources are managed declaratively using Terraform for consistency and version control.

## 2. System & Data Flow

The following diagram illustrates the flow of data and interactions between the major components of the CityPulse system.

```mermaid
graph TD
    subgraph "Clients"
        A[Web Frontend - Next.js]
        B[Mobile App - Flutter]
    end

    subgraph "Backend Services"
        C[API Layer - Cloud Run/Functions]
        D[Firebase Authentication]
    end

    subgraph "Data Layer"
        E[Firestore]
        F[Google BigQuery]
        G[Cloud Storage]
    end

    subgraph "Async Processing"
        H[Google Cloud Pub/Sub]
        I[Dataflow Pipelines]
    end

    subgraph "AI/ML Services"
        J[Vertex AI - Gemini, Vision, NLP]
    end

    A -->|REST API Calls| C
    B -->|REST API Calls| C
    A -->|Directly for Real-time| E
    B -->|Directly for Real-time| E

    C -->|CRUD & Business Logic| E
    C -->|Analytics Queries| F
    C -->|Media Uploads| G
    C -->|Authentication| D
    C -->|Publish Events| H

    H -->|Trigger| I
    I -->|Process & Enrich| I
    I -->|Store Historical Data| F
    I -->|Update Real-time Views| E
    I -->|Analyze Media| J

    J -->|Store Insights| F
    J -->|Store Insights| E

    A & B -->|Authenticate with| D
```text
**Flow Description**:

1.  **User Interaction**: Users interact with the **Web Frontend** or **Mobile App**. They authenticate using **Firebase Authentication**.
2.  **API Communication (Planned)**: For most actions (submitting reports, fetching historical data), clients will make calls to the **API Layer**. Currently, for real-time updates (live map data), clients subscribe directly to **Firestore**.
3.  **Synchronous Processing**: The **API Layer** handles business logic, performs CRUD operations on **Firestore**, queries **BigQuery** for analytics, and manages media uploads to **Cloud Storage**.
4.  **Asynchronous Processing**: For data that requires heavy processing, the API Layer publishes messages to **Pub/Sub**.
5.  **Data Pipelines**: **Dataflow Pipelines** consume messages from Pub/Sub, performing tasks like data cleaning, normalization, and enrichment.
6.  **AI/ML Analysis**: Pipelines send data to **Vertex AI** services (Gemini, Vision) for analysis. The resulting insights (summaries, tags, sentiment) are stored back in Firestore and BigQuery.
7.  **Data Storage**: Processed data is stored in **BigQuery** for long-term analytics and **Firestore** for real-time access.

## 3. Client Architecture

### 3.1. Web Frontend (`src/`)

The frontend is a modern web application built with **Next.js** and **TypeScript**.

-   **Framework**: Next.js with the App Router.
-   **UI**: React, Tailwind CSS, and potentially a component library like Material UI.
-   **Data Fetching**: Uses a combination of direct Firestore SDK access for real-time data and `fetch` calls to the backend REST API for other operations.
-   **Key Features**: Interactive map (Google Maps API), event visualization (markers, heatmaps), citizen reporting forms, and analytics dashboards.
-   **Deployment**: Deployed via Vercel or Firebase Hosting with CDN for global performance.

### 3.2. Mobile App (Planned)

A cross-platform mobile application is planned using **Flutter**.

-   **Platform**: iOS and Android from a single codebase.
-   **Key Features**: Intuitive UI for citizen reporting (including media capture), push notifications for alerts (via FCM), and offline capabilities.
-   **Backend Communication**: Interacts with the same REST API and Firebase services as the web frontend.

## 4. Backend Architecture

### 4.1. API Layer (Planned)

A set of secure, scalable REST APIs is planned to be built using **Google Cloud Run** or **Cloud Functions**.

-   **Technology**: Node.js, Python, or Go.
-   **Responsibilities**:
    -   Exposing CRUD endpoints for Events, Users, and Feedback.
    -   Handling user authentication and role-based authorization (Citizen, Authority, Admin).
    -   Serving aggregated analytics data from BigQuery.
    -   Validating input and enforcing business logic.
-   **Specification**: An OpenAPI/Swagger specification will define the API contracts.

### 4.2. Data Processing Pipelines (`data_models/data_ingestion/`)

These are asynchronous, serverless pipelines built with **Apache Beam** (Python SDK) and run on **Google Cloud Dataflow**.

-   **Source**: Subscribe to Pub/Sub topics for various data streams (citizen reports, social media, IoT, official feeds).
-   **Processing**: Perform robust data validation (using Pydantic models), cleaning, normalization, geotagging, and trigger AI/ML analysis.
-   **Sink**: Load processed data into BigQuery and update Firestore collections.
-   **Resilience**: Utilize dead-letter queues to capture and isolate the original problematic data without interrupting the main pipeline flow, ensuring robust error handling and easier debugging.
-   **Configuration**: Pipelines are highly configurable via command-line arguments, allowing for flexibility in different environments (e.g., specifying input topics, output tables, or schema paths).

## 5. AI/ML Integration (Partially Implemented)

The intelligence layer leverages **Vertex AI** to automate analysis and generate insights. Sentiment analysis is implemented, while other features are planned.

-   **Multimodal Processing**:
    -   **Text (Gemini)**: Summarization, classification, and narrative generation for reports.
    -   **Images/Video (Vision API)**: Object detection (e.g., potholes, graffiti) and feature extraction.
    -   **NLP**: Sentiment analysis on social media feeds.
-   **Event Clustering**: Algorithms to group related events based on spatial-temporal proximity and AI-generated tags.
-   **Feedback Loop**: The system is designed to capture user feedback on AI insights to enable future model retraining.

## 6. Data Layer

-   **Firestore**: Used as the primary operational database for real-time data. It stores user profiles, active event data, feedback, and user preferences. Its real-time listeners power live updates on the clients.
-   **BigQuery**: Serves as the analytical data warehouse. It stores historical event data, AI-generated insights, and aggregated metrics. Tables are partitioned and clustered for query performance and cost-efficiency.
-   **Cloud Storage**: Stores user-uploaded multimedia files (images, videos) associated with reports.

## 7. Infrastructure (`infra/`)

All cloud resources are defined declaratively in **Terraform**. This IaC approach ensures the environment is version-controlled, reproducible, and easy to manage. Key managed resources include VPC networking, databases, Pub/Sub topics, IAM roles, and monitoring dashboards.
