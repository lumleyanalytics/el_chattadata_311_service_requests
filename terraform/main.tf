# main.tf

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Call the Terraform Service Account Module
module "terraform_service_account" {
  source = "./terraform_service_account_module"
}

# Call the Project Permissions Module
module "project_permissions" {
  source           = "./project_permissions_module"
  project_id       = var.project_id
  terraform_sa_email = module.terraform_service_account.terraform_sa_email
}

# Call the Project Data Module
module "project_data" {
  source     = "./project_data_module"
  project_id = var.project_id
}

# Call the GCS Bucket Module for Each Bucket
module "gcs_bucket_lumley_analytics_seeds" {
  source      = "./gcs_module"
  project_id  = var.project_id
  region      = var.region
  bucket_name = "lumley_analytics_seeds"
}

module "gcs_bucket_lumley_analytics_cloud_run_functions" {
  source      = "./gcs_module"
  project_id  = var.project_id
  region      = var.region
  bucket_name = "lumley-analytics-cloud-run-functions"
}

# BigQuery Dataset Module
module "bigquery" {
  source      = "./bigquery_module"
  project_id  = var.project_id
  region      = var.region
  dataset_id  = var.bigquery_dataset_id
  table_id = var.bigquery_table_id
}

# Permissions Module
module "permissions" {
  source                    = "./permissions_module"
  project_id                = var.project_id
  region                    = var.region
}

# Cloud Functions Module
module "cloud_functions" {
  source           = "./cloud_functions_module"
  project_id       = var.project_id
  region           = var.region
  gcs_bucket_name  = "lumley-analytics-cloud-run-functions"
  function_prefix  = "lumley-analytics-functions"
}

# Google Secrets Manager Module
module "google_secrets" {
  source     = "./google_secrets_module"
  project_id = var.project_id

  secrets = {
    CHATTADATA_API_KEY = var.chattadata_api_key
    SNOWFLAKE_USER     = var.snowflake_user
    SNOWFLAKE_PASSWORD = var.snowflake_password
    SNOWFLAKE_ACCOUNT  = var.snowflake_account
  }
}

# Service Accounts Module
module "service_accounts" {
  source     = "./service_accounts_module"
  project_id = var.project_id
}

# Cloud Run Module
module "cloud_run" {
  source        = "./cloud_run_module"
  project_id    = var.project_id
  region        = var.region
  api_url       = var.api_url
  api_key       = var.api_key
  gcs_bucket    = var.gcs_bucket
  gcs_file_name = var.gcs_file_name
}

# Cloud Scheduler Module
module "cloud_scheduler" {
  source                          = "./cloud_scheduler_module"
  scheduler_service_account_email = google_service_account.scheduler_sa.email
}
