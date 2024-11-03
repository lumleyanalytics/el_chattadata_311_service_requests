# main.tf

# Create Composer Environment
resource "google_composer_environment" "composer" {
  name    = var.environment_name
  project = var.project_id
  region  = var.region

  config {
    software_config {
      image_version = "composer-2.9.9-airflow-2.9.3"

      # Setting environment variables for Cloud Function URLs
      env_variables = {
        FETCH_TO_GCS_URL       = var.fetch_to_gcs_url
        GCS_TO_BIGQUERY_URL    = var.gcs_to_bigquery_url
        GCS_TO_SNOWFLAKE_URL   = var.gcs_to_snowflake_url
      }
    }
  }
}


