# bigquery_module/variables.tf
variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "dataset_id" {
  type = string
}

# bigquery_module/variables.tf
variable "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "bigquery_table_id" {
  description = "BigQuery table ID"
  type        = string
}
