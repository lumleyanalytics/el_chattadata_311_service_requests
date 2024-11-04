# root/variables.tf
variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
  default     = "lumley-analytics"
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-east4"
}

variable "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "chatt_311_service_requests"
}

variable "bigquery_table_id" {
  description = "BigQuery table ID"
  type        = string
  default     = "tst_311_requests"
}
