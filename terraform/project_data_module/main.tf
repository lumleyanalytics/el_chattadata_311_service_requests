# project_data_module/main.tf

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

data "google_project" "project" {
  project_id = var.project_id
}

output "project_number" {
  value = data.google_project.project.number
}
