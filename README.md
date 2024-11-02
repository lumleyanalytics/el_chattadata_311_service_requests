
# Chattanooga 311 Data Pipeline

This repository contains the infrastructure and code to deploy an Airflow pipeline on Google Cloud, using Cloud Composer, BigQuery, GCS, and Snowflake. The infrastructure is managed by Terraform, and all code is versioned in this repository. The pipeline processes data from Chattanooga’s Open Data API and loads it into BigQuery and Snowflake.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Google Cloud Setup](#google-cloud-setup)
4. [Terraform Setup](#terraform-setup)
5. [Deploying with Terraform](#deploying-with-terraform)
6. [Airflow Pipeline](#airflow-pipeline)
7. [CI/CD with GitHub Actions](#cicd-with-github-actions)

## Project Structure

```plaintext
.
├── dags/                        # Airflow DAGs for the data pipeline
│   └── chattanooga_311_data_pipeline.py
├── scripts/                     # Python scripts used by the DAGs
│   ├── fetch_to_gcs.py
│   ├── gcs_to_bigquery.py
│   └── gcs_to_snowflake.py
├── terraform/                   # Terraform modules and configurations
│   ├── main.tf                  # Main Terraform config to set up GCP resources
│   ├── composer_module/         # Cloud Composer setup
│   ├── gcs_module/              # GCS bucket setup
│   ├── bigquery_module/         # BigQuery dataset and table definitions
│   ├── permissions_module/      # IAM role assignments
│   └── variables.tf             # Terraform variables
└── README.md                    # Project documentation
```

## Prerequisites

1. **Google Cloud Account** with permissions for Cloud Composer, BigQuery, GCS, and IAM.
2. **Terraform** installed on your local machine.
3. **Python 3.10** installed and configured, with necessary dependencies for the scripts in `scripts/`.
4. **Google Cloud SDK** for managing and authenticating to Google Cloud from the command line.

## Google Cloud Setup

1. **Create a Google Cloud Project**: 
   - Follow instructions to create a Google Cloud project.
   
2. **Enable APIs**:
   - Enable the following APIs:
     - Cloud Composer API
     - BigQuery API
     - Cloud Storage API
     - Cloud Run API (optional)

3. **Service Account and IAM**:
   - Create a service account with roles for Composer, BigQuery, GCS, and any other services you need. 
   - Update the permissions in the `terraform/permissions_module/` to match your requirements.

## Terraform Setup

1. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   ```

2. **Configure Variables**:
   - Open `variables.tf` and set the values for your Google Cloud project, region, and other configurations.
   - You can override these by creating a `terraform.tfvars` file in the `terraform` folder.

## Deploying with Terraform

1. **Preview Changes**:
   - Run `terraform plan` to see the resources that will be created and configured on Google Cloud.

2. **Apply Changes**:
   - Run `terraform apply` to deploy the resources. Confirm when prompted.

3. **Verify Deployment**:
   - After deployment, go to the [Google Cloud Console](https://console.cloud.google.com/) and confirm that Cloud Composer and other resources are created as expected.

## Airflow Pipeline

The Airflow DAG for the pipeline is located in `dags/chattanooga_311_data_pipeline.py`. 

1. **DAG Overview**:
   - `fetch_to_gcs`: Fetches data from the Chattanooga Open Data API and uploads it to Google Cloud Storage.
   - `gcs_to_bigquery`: Loads data from GCS into BigQuery.
   - `gcs_to_snowflake`: Loads data from GCS into Snowflake.

2. **DAG Setup**:
   - The `dags/` folder should be synced with the DAGs bucket for Cloud Composer. This is usually done by Composer automatically.

## CI/CD with GitHub Actions

To automate deployments and manage the Terraform state, set up GitHub Actions.

1. **GitHub Actions Workflow**:
   - Create a `.github/workflows/terraform.yml` workflow file to automatically run `terraform plan` and `terraform apply` on PRs or pushes to the `main` branch.

2. **Secrets**:
   - Add Google Cloud credentials and other secrets in GitHub as repository secrets.

3. **Sample GitHub Actions Workflow**:

   ```yaml
   name: Terraform CI/CD

   on:
     push:
       branches:
         - main
     pull_request:
       branches:
         - main

   jobs:
     terraform:
       name: Terraform Plan and Apply
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v2

         - name: Set up Google Cloud SDK
           uses: google-github-actions/setup-gcloud@v0
           with:
             project_id: ${{ secrets.GCP_PROJECT_ID }}
             service_account_key: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
             export_default_credentials: true

         - name: Set up Terraform
           uses: hashicorp/setup-terraform@v1

         - name: Terraform Init
           run: terraform init
           working-directory: ./terraform

         - name: Terraform Plan
           run: terraform plan -out tfplan
           working-directory: ./terraform

         - name: Terraform Apply
           if: github.ref == 'refs/heads/main'
           run: terraform apply tfplan
           working-directory: ./terraform
   ```

## Future Improvements

- **Cloud Run**: Consider deploying data fetch operations on Cloud Run for independent processing.
- **Data Validation**: Implement data validation in the Airflow DAG to verify data consistency before loading.
- **Enhanced Monitoring**: Use Google Cloud Monitoring to track pipeline performance and alerts.

## Troubleshooting

- If DAGs don’t appear in Airflow, check the GCS bucket for correct syncing with Cloud Composer.
- For Terraform issues, inspect logs from `terraform plan` and `terraform apply` for errors.
