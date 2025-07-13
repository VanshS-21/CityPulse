# Contributing to CityPulse

First off, thank you for considering contributing to CityPulse! It's people like you that make CityPulse such a great
tool. We welcome any form of contribution, from reporting bugs and submitting feedback to writing code and improving
documentation.

## Table of Contents

-    [Code of Conduct](#code-of-conduct)
-    [Getting Started](#getting-started)
    -    [Prerequisites](#prerequisites)
    -    [Fork & Clone](#fork--clone)
-    [Development Environment Setup](#development-environment-setup)
    -    [Frontend (Next.js)](#frontend-nextjs)
    -    [Backend Data Pipelines (Python)](#backend-data-pipelines-python)
    -    [Backend API Layer (Planned)](#backend-api-layer-planned)
    -    [Mobile App (Planned)](#mobile-app-planned)
-    [How to Contribute](#how-to-contribute)
    -    [Reporting Bugs](#reporting-bugs)
    -    [Suggesting Enhancements](#suggesting-enhancements)
    -    [Making Code Contributions](#making-code-contributions)
-    [Pull Request Process](#pull-request-process)
-    [Coding Style Guides](#coding-style-guides)
    -    [TypeScript/JavaScript](#typescriptjavascript)
    -    [Python](#python)
    -    [API Design](#api-design)

## Code of Conduct

This project and everyone participating in it is governed by the [CityPulse Code of Conduct](CODE_OF_CONDUCT.md). By
participating, you are expected to uphold this code. Please report unacceptable behavior.

## Getting Started

### Prerequisites

Make sure you have the following tools installed on your system:

-    Node.js (v18 or later)
-    Python (v3.11 or later)
-    Terraform (v1.0 or later)
-    Google Cloud SDK (`gcloud`)
-    Flutter SDK (for mobile development)

### Fork & Clone

1.  Fork the repository on GitHub.
1.  Clone your fork locally: `git clone <https://github.com/your-username/CityPulse.git`>

## Development Environment Setup

### Frontend (Next.js)

```bash

## Navigate to the project root

cd CityPulse

## Install dependencies

npm install

## Run the development server

npm run dev
```text

## Backend Data Pipelines (Python)

Refer to the `data_models/README.md`for detailed instructions on setting up the Python environment and running the data
ingestion pipelines locally.

### Backend API Layer (Planned)

When contributing to the backend API (Cloud Run/Functions):

1.  Set up a local development server for the chosen framework (e.g., Express for Node.js, FastAPI for Python).
1.  Use tools like the Firebase Local Emulator Suite to mock cloud services.
1.  Ensure you have authenticated with the Google Cloud SDK.

### Mobile App (Planned)

To contribute to the Flutter mobile app:

1.  Ensure you have the Flutter SDK and its dependencies (Xcode for iOS, Android Studio for Android) installed.
1.  Run`flutter doctor`to verify your setup.
1.  Open the project in your preferred editor (VS Code or Android Studio) and run it on an emulator or a physical device.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub and provide as much detail as possible, including steps to reproduce,
expected behavior, and screenshots.

### Suggesting Enhancements

We welcome suggestions for new features or improvements. Please open an issue to start a discussion about your idea.

### Making Code Contributions

1.  Create a new branch for your feature or bug fix:`git checkout -b feature/your-feature-name`1.  Make your changes, following the coding style guides.
1.  Commit your changes with a descriptive commit message.
1.  Push your branch to your fork:`git push origin feature/your-feature-name`1.  Open a pull request to the`main`branch of the original repository.

## Pull Request Process

1.  Ensure that your code lints and any relevant tests pass.
1.  Update the`README.md`or other documentation with details of changes to the interface, this includes new environment
variables, new public API routes, etc.

1.  Your pull request will be reviewed by the maintainers. You may be asked to make changes before it can be merged.

## Coding Style Guides

### TypeScript/JavaScript

We use ESLint and Prettier to enforce a consistent coding style. Please run`npm run lint`and`npm run format`before
committing your changes.

### Python

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for all Python code. We use`black`for formatting and`flake8` for linting.

### API Design

For contributions to the backend API:

-  **Specification First**: All new endpoints or changes to existing ones must be documented in the OpenAPI/Swagger
specification first.

-    **RESTful Principles**: Follow RESTful design principles for creating scalable and maintainable APIs.
-    **Security**: Ensure all endpoints have proper authentication and authorization checks.
