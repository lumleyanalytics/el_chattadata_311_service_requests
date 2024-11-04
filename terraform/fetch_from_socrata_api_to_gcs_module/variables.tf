# fetch_from_api_to_gcs_module/variables.tf

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

variable "api_url" {
  description = "The API URL to fetch data from"
  type        = string
  default     = "https://www.chattadata.org/resource/8qb9-5fja.json"
}

variable "gcs_bucket" {
  description = "The GCS bucket to store fetched data"
  type        = string
  default     = "lumley_analytics_seeds"
}
