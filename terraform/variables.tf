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
  default     = "src_chattadata_311_service_requests"
}

variable "github_repo_owner" {
  description = "Owner of the GitHub repository"
  type        = string
  default     = "lumleyanalytics"
}

variable "github_repo_name" {
  description = "Name of the GitHub repository"
  type        = string
  default     = "el_chattadata_311_service_requests"
}
variable "chattadata_api_key" {
  description = "API Key for Chattadata"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake user"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
}

variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
}

