# cloud_functions_module/variables.tf

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The region for Cloud Functions"
  type        = string
}

variable "gcs_bucket_name" {
  description = "The GCS bucket where function code is stored"
  type        = string
}

variable "function_prefix" {
  description = "Prefix for naming each Cloud Function"
  type        = string
  default     = "my-functions"
}

# cloud_functions_module/variables.tf

variable "fetch_to_gcs_url" {
  description = "URL for the Fetch to GCS function"
  type        = string
}

variable "gcs_to_bigquery_url" {
  description = "URL for the GCS to BigQuery function"
  type        = string
}

variable "gcs_to_snowflake_url" {
  description = "URL for the GCS to Snowflake function"
  type        = string
}

