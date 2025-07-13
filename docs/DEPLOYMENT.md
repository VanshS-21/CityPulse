# CityPulse Deployment Guide

This guide provides comprehensive instructions for deploying the CityPulse application. It is divided into two main
sections: deploying the Next.js frontend to Vercel and deploying the Apache Beam data pipelines to Google Cloud
Dataflow.

## 1. Frontend Deployment (Next.js on Vercel)

Vercel is the recommended platform for deploying the CityPulse Next.js frontend due to its seamless integration with
Next.js, automatic CI/CD, and global CDN.

### Prerequisites

-  A Vercel account.
-  A GitHub, GitLab, or Bitbucket account with the CityPulse repository.

### Step-by-Step Instructions

1.  **Import Project to Vercel:**-    Log in to your Vercel account.
    -    From the dashboard, click "Add New..." -> "Project".
-  Connect your Git provider and select the CityPulse repository. Vercel will automatically detect that it is a Next.js
project.

1.**Configure Project Settings:**-**Framework Preset:**Should be automatically set to `Next.js`.
    -**Build Command:**`npm run build` (or your custom build script).
    -**Output Directory:**`.next` (default for Next.js).
    -**Install Command:**`npm install`.

1.**Set Environment Variables:**-    In the project settings on Vercel, navigate to the "Environment Variables" section.
    -    Add all required environment variables for the frontend application. These may include:
        -    `NEXT_PUBLIC_FIREBASE_API_KEY`: Your Firebase project's API key.
        -    `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`: Your Firebase project's auth domain.
        -    `NEXT_PUBLIC_FIREBASE_PROJECT_ID`: Your Firebase project's ID.
        -    `NEXT_PUBLIC_SENTRY_DSN`: Your Sentry project's DSN for error monitoring.

1.**Deploy:**-    Click the "Deploy" button. Vercel will start the build and deployment process.
-  Once complete, you will be provided with a public URL for your deployed application. Vercel will automatically
redeploy the application on every push to the main branch.

## 2. Backend Deployment (Apache Beam on Google Cloud Dataflow)

The backend consists of Apache Beam pipelines that process streaming data. These are best deployed as templates to
Google Cloud Dataflow for scalable, managed execution.

### Prerequisites 2

-  A Google Cloud Platform (GCP) project with billing enabled.
-  The `gcloud` CLI installed and authenticated (`gcloud auth login`).
-  A Google Cloud Storage (GCS) bucket to store the pipeline templates.

### Step-by-Step Instructions 2

1.**Package the Pipeline as a Flex Template:**-  Dataflow Flex Templates allow you to package your pipeline and its dependencies in a Docker image, which can then be
run from anywhere.

    -    Create a `Dockerfile`in the`data_models`directory:```Dockerfile
        FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

## Set the working directory
        WORKDIR /template

## Copy the requirements file and install dependencies
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

## Copy the pipeline code
        COPY . .

## Set the entrypoint for the template
        ENV FLEX_TEMPLATE_PYTHON_PY_FILE="data_ingestion/iot_pipeline.py"
        ```-    Build the Docker image and push it to Google Container Registry (GCR):```bash
## Set your GCP Project ID and desired image name
        export PROJECT_ID="your-gcp-project-id"
        export IMAGE_NAME="citypulse-iot-pipeline"
        export BUCKET_NAME="your-gcs-bucket-for-templates"

## Build the Docker image
        docker build . -t gcr.io/${PROJECT_ID}/${IMAGE_NAME}

## Push the image to GCR
        docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}
        ```1.**Create the Flex Template Specification:**-  Create a JSON file (e.g.,`iot_pipeline_template.json`) and upload it to your GCS bucket. This file tells Dataflow
where to find your Docker image and what parameters it expects.
        ```json
        {
            "image": "gcr.io/your-gcp-project-id/citypulse-iot-pipeline",
            "sdk_info": { "language": "PYTHON" },
            "metadata": {
                "name": "CityPulse IoT Ingestion Pipeline",
                "description": "Processes and stores IoT data from Pub/Sub into Firestore.",
                "parameters": [{
                        "name": "input_subscription",
                        "label": "Input Pub/Sub Subscription",
                        "help_text": "The Pub/Sub subscription to read raw IoT data from.",
                        "is_optional": false
                    },
                    {
                        "name": "output_collection",
                        "label": "Output Firestore Collection",
                        "help_text": "The Firestore collection to write processed events to.",
                        "is_optional": false
                    }]
            }
        }
        ```1.**Run the Dataflow Job from the Template:**-    You can now launch the pipeline using the`gcloud`CLI:```bash
        gcloud dataflow flex-template run "iot-pipeline-`date +%Y%m%d-%H%M%S`" \

            - -template-file-gcs-location "gs://${BUCKET_NAME}/iot_pipeline_template.json" \
            - -project "${PROJECT_ID}" \
            - -region "your-gcp-region" \
            - -parameters input_subscription="projects/${PROJECT_ID}/subscriptions/your-iot-subscription" \
            - -parameters output_collection="events"
        ```

1.**Monitor the Job:**
    -    Navigate to the Dataflow section in the Google Cloud Console.
    -    You will see your running job and can monitor its progress, inspect logs, and view metrics.

Repeat this process for each data pipeline (`citizen_report_pipeline`, `social_media_pipeline`, etc.) by creating a
corresponding Dockerfile, template spec, and launch command.
