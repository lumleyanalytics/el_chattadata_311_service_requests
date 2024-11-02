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
