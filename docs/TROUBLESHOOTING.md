# CityPulse Troubleshooting Guide

This guide is intended to help developers resolve common issues encountered while working on the CityPulse project. It
covers problems related to the development environment, data pipelines, and application deployment.

## 1. Development Environment Setup

### Issue: `gcloud`command not found

-    **Symptom:**Your terminal returns an error like`bash: gcloud: command not found`or similar.
-**Solution:**The Google Cloud SDK is not installed or not in your system's PATH.
    1.  Follow the official instructions to [install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
    2.  After installation, restart your terminal or source your shell profile file (e.g.,`source ~/.bashrc`).
    3.  Verify the installation by running `gcloud --version`.

### Issue: Firebase authentication errors locally

-**Symptom:**The frontend application fails to connect to Firebase services, showing authentication or permission
errors in the console.

-**Solution:** Your local environment is not correctly authenticated with Google Cloud.
1.  Run `gcloud auth application-default login`. This will open a browser window for you to log in to your Google
account.

1.  This command creates a local credential file that Firebase and other Google Cloud client libraries can use
automatically.

1.  Ensure your `.env.local`file in the`src`directory contains the correct`NEXT_PUBLIC_FIREBASE_*` variables for your
project.

### Issue: Python dependency conflicts

-    **Symptom:**`pip install`fails with messages about conflicting dependency versions.
-**Solution:**It is highly recommended to use a virtual environment to isolate project dependencies.
    1.  Navigate to the`data_models`directory.
    2.  Create a virtual environment:`python -m venv .venv`3.  Activate it:
        -    Windows:`.venv\Scripts\activate`-    macOS/Linux:`source .venv/bin/activate`4.  Install the dependencies within the activated environment:`pip install -r requirements.txt`## 2. Running Data Pipelines

### Issue:`PipelineOptions`error when running a pipeline

-**Symptom:**An Apache Beam pipeline fails on launch with an error related to missing`PipelineOptions` or incorrect
project/region settings.

-**Solution:**The pipeline is missing necessary command-line arguments to configure the runner and GCP settings.
    -    When running a pipeline that interacts with GCP services (even locally), you must provide core arguments.
    -**Example:**```bash
        python -m data_ingestion.iot_pipeline \

          - -runner DataflowRunner \
          - -project your-gcp-project-id \
          - -region your-gcp-region \
          - -temp_location gs://your-gcs-bucket/temp \
          - -input_subscription projects/your-gcp-project-id/subscriptions/your-iot-subscription \
          - -output_collection events
        ```

    -    Ensure the service account you are using has the "Dataflow Worker" and other necessary roles.

### Issue: Dataflow job fails with "permission denied" on a GCP service

-**Symptom:**A Dataflow job starts but quickly fails with logs indicating permission denied errors when trying to
access Pub/Sub, Firestore, or BigQuery.

-**Solution:**The Dataflow worker service account lacks the required IAM permissions.
    1.  Go to the IAM & Admin section in the Google Cloud Console.
1.  Find the service account used by Dataflow. By default, this is your project's Compute Engine default service account
(`<project-number>-compute@developer.gserviceaccount.com`). It is better to use a dedicated service account.

    2.  Ensure this service account has the following roles:
        -    `roles/dataflow.worker`: For running Dataflow jobs.
        -    `roles/pubsub.subscriber`: To read from Pub/Sub subscriptions.
        -    `roles/datastore.user`: To write to Firestore.
        -    `roles/bigquery.dataEditor`: To write to BigQuery tables.

## 3. Application Deployment

### Issue: Vercel build fails

-**Symptom:**The deployment process on Vercel fails during the build step.
-**Solution:**1.**Check Logs:**The Vercel deployment logs are the best place to start. They will usually contain the specific error
message (e.g., TypeScript error, missing dependency).

1.**Run Build Locally:**Try to replicate the issue by running `npm run build`on your local machine. This can help you
debug faster.

1.**Check Environment Variables:** Ensure all required`NEXT_PUBLIC_*`environment variables are correctly set in the
Vercel project settings. A missing variable can often cause build failures.

### Issue: Dataflow Flex Template job fails to launch

-  **Symptom:**The`gcloud dataflow flex-template run`command fails immediately with an error about the template being
invalid or not found.

-**Solution:**1.**Check GCS Path:**Double-check that the`--template-file-gcs-location`path is correct and that the JSON template
file exists at that location.

1.**Check Docker Image Path:**In your template JSON file, verify that the`image`path points to a valid Docker image
in Google Container Registry (GCR) that you have permission to access.

    2.**Check API Enablement:** Ensure the`Dataflow API`and`Cloud Build API` are enabled in your GCP project.
