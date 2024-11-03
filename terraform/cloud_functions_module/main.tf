# cloud_functions_module/main.tf

# Define Cloud Function for fetch_to_gcs
resource "google_cloudfunctions_function" "fetch_to_gcs" {
  name        = "${var.function_prefix}-fetch-to-gcs"
  runtime     = "python310"
  entry_point = "main"
  region      = var.region

  source_archive_bucket = var.gcs_bucket_name
  source_archive_object = "fetch_to_gcs.zip"

  trigger_http = true

  environment_variables = {
    GCS_BUCKET = var.gcs_bucket_name
  }
}

# Define Cloud Function for gcs_to_bigquery
resource "google_cloudfunctions_function" "gcs_to_bigquery" {
  name        = "${var.function_prefix}-gcs-to-bigquery"
  runtime     = "python310"
  entry_point = "main"
  region      = var.region

  source_archive_bucket = var.gcs_bucket_name
  source_archive_object = "gcs_to_bigquery.zip"

  trigger_http = true
}

# Define Cloud Function for gcs_to_snowflake
resource "google_cloudfunctions_function" "gcs_to_snowflake" {
  name        = "${var.function_prefix}-gcs-to-snowflake"
  runtime     = "python310"
  entry_point = "main"
  region      = var.region

  source_archive_bucket = var.gcs_bucket_name
  source_archive_object = "gcs_to_snowflake.zip"

  trigger_http = true
}

# Define Cloud Function for el_311_service_requests
resource "google_cloudfunctions_function" "el_311_service_requests" {
  name        = "${var.function_prefix}-el_311_service_requests"
  runtime     = "python310"
  entry_point = "main"
  region      = var.region

  source_archive_bucket = var.gcs_bucket_name
  source_archive_object = "el_311_service_requests.zip"

  trigger_http = true
}