# CityPulse Google Cloud Infrastructure Setup

This guide provides instructions for provisioning the Google Cloud infrastructure for the CityPulse
platform using Terraform.

## 1. Prerequisites

Before you begin, ensure you have the following installed and configured:

-     [Terraform](https://www.terraform.io/downloads.html) (v1.0.0 or later)
-     [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
-     A Google Cloud project with billing enabled.

## 2. Authentication

Authenticate with Google Cloud. This command will open a browser window for you to log in to your
Google account.

````bash
gcloud auth application-default login
gcloud auth login
```text

## 3. Configuration

All infrastructure variables are defined in `terraform.tfvars`. To get started, copy the example file:

```bash
cp terraform.tfvars.example terraform.tfvars
```text

Now, open `terraform.tfvars`and update the following values for your environment:

- `project_id`: Your Google Cloud project ID.
-     `region`: The primary region for your resources (e.g., `us-central1`).
-     `zone`: The primary zone within your region (e.g., `us-central1-a`).
-     `alert_email`: The email address where monitoring alerts will be sent.

## 4. Deployment

Follow these steps to deploy the infrastructure:

1.  **Initialize Terraform**:
    Downloads the necessary provider plugins.

    ```bash
    terraform init
    ```1.  **Create an Execution Plan**:
    Reviews the changes that will be made to your infrastructure.```bash
    terraform plan
    ```1.  **Apply the Plan**:
    Provisions the resources in your Google Cloud project. You will be prompted to confirm the changes.```bash
    terraform apply
    ```

## 5. Infrastructure Overview

This Terraform configuration will provision the following resources:

-     **APIs**: Enables all necessary services (Pub/Sub, BigQuery, Firestore, etc.).
-     **Service Account**: Creates a dedicated service account (`citypulse-sa`) with appropriate IAM roles.
-     **Pub/Sub**: A topic for data ingestion (`citypulse-data-ingestion`).
-     **BigQuery**: A dataset for analytics (`citypulse_analytics`).
-     **Cloud Storage**: A bucket for multimedia files.
-     **Firestore**: A native mode database.
-     **Vertex AI**: A feature store for machine learning.
-     **Monitoring**: A custom dashboard and alert policies for key metrics.

## 6. Clean Up

To decommission all resources created by this configuration, run the following command. **Use with caution, as this
action is irreversible.**

```bash
terraform destroy
```text

-   [Terraform Documentation](https://www.terraform.io/docs/index.html)
-   [Google Cloud Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
-   [Google Cloud Best Practices](https://cloud.google.com/docs/terraform/best-practices-for-terraform)
````
