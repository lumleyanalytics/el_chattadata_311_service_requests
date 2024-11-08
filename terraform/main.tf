# main.tf

provider "google" {
  project   = var.project_id
  region    = var.region
}

provider "google-beta" {
  project   = var.project_id
  region    = var.region
}

# Step 1: Create a Service Account
resource "google_service_account" "terraform_sa" {
  account_id   = "terraform-admin-sa"
  display_name = "Terraform Admin Service Account"
}

# Step 2: Create and Download Key for the Service Account
resource "google_service_account_key" "terraform_sa_key" {
  service_account_id = google_service_account.terraform_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Output the service account key for setting up GOOGLE_APPLICATION_CREDENTIALS
output "service_account_key" {
  value     = google_service_account_key.terraform_sa_key.private_key
  sensitive = true
}

# Step 3: Grant Required Roles to the Service Account
resource "google_project_iam_member" "terraform_sa_owner" {
  project = var.project_id
  role    = "roles/owner"
  member  = "serviceAccount:${google_service_account.terraform_sa.email}"
}

# Step 4: Add Required Role for the Composer GKE Service Account

# Get the project number dynamically
data "google_project" "project" {
  project_id = var.project_id
}

# Grant the Composer GKE service account the roles/composer.ServiceAgentV2Ext role
resource "google_project_iam_member" "composer_gke_service_agent" {
  project = var.project_id
  role    = "roles/composer.ServiceAgentV2Ext"
  member  = "serviceAccount:service-${data.google_project.project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

# Step 5: Set up Cloud Composer, GCS, BigQuery, and Permissions Modules

# Composer Module
module "composer" {
  source             = "./composer_module"
  project_id         = var.project_id
  region             = var.region
  environment_name   = var.composer_environment_name

  # Pass the Cloud Function URLs as variables
  fetch_to_gcs_url       = module.cloud_functions.fetch_to_gcs_url
  gcs_to_bigquery_url    = module.cloud_functions.gcs_to_bigquery_url
  gcs_to_snowflake_url   = module.cloud_functions.gcs_to_snowflake_url

}

# GCS Bucket Module - lumley_analytics_seeds
module "gcs_bucket_lumley_analytics_seeds" {
  source      = "./gcs_module"
  project_id  = var.project_id
  region      = var.region
  bucket_name = "lumley_analytics_seeds"
}

# GCS Bucket Module - lumley-analytics-cloud-run-functions
module "gcs_bucket_lumley-analytics-cloud-run-functions" {
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
}

# Permissions Module - uses the service account created earlier
module "permissions" {
  source                    = "./permissions_module"
  project_id                = var.project_id
  region                    = var.region
  composer_service_account  = google_service_account.terraform_sa.email
  composer_environment_name = var.composer_environment_name
}

module "cloud_functions" {
  source          = "./cloud_functions_module"
  project_id      = var.project_id
  region          = var.region
  gcs_bucket_name = module.gcs_bucket_lumley-analytics-cloud-run-functions.bucket_name  # Use the output from gcs_module
  function_prefix = "lumley-analytics-functions"
}

module "google_secrets" {
  source     = "./google_secrets_module"
  project_id = var.project_id

  secrets = {
    CHATTADATA_API_KEY = var.chattadata_api_key
    SNOWFLAKE_USER = var.snowflake_user
    SNOWFLAKE_PASSWORD = var.snowflake_password
    SNOWFLAKE_ACCOUNT = var.snowflake_account
  }
}

