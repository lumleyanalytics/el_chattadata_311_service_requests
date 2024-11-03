# composer_module/variables.tf
variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment_name" {
  type = string
}

variable "fetch_to_gcs_url" {
  description = "URL for the fetch_to_gcs Cloud Function"
  type        = string
}

variable "gcs_to_bigquery_url" {
  description = "URL for the gcs_to_bigquery Cloud Function"
  type        = string
}

variable "gcs_to_snowflake_url" {
  description = "URL for the gcs_to_snowflake Cloud Function"
  type        = string
}
