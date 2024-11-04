# project_permissions_module/main.tf

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "terraform_sa_email" {
  description = "Terraform Admin Service Account email"
  type        = string
}

resource "google_project_iam_member" "terraform_sa_owner" {
  project = var.project_id
  role    = "roles/owner"
  member  = "serviceAccount:${var.terraform_sa_email}"
}
