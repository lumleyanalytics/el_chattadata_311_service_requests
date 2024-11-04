variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
}

variable "api_url" {
  description = "API endpoint for fetching data"
  type        = string
}

variable "api_key" {
  description = "API key for the data source"
  type        = string
}

variable "gcs_bucket" {
  description = "GCS bucket to store data"
  type        = string
}

variable "gcs_file_name" {
  description = "Name of the GCS file to store data"
  type        = string
}

# GitHub repository details for Cloud Build
variable "github_repo_owner" {
  description = "GitHub owner (user or organization) of the repo"
  type        = string
}

variable "github_repo_name" {
  description = "GitHub repository name"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch to monitor for Docker image rebuild"
  type        = string
  default     = "main"
}
