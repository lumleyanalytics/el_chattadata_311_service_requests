# permissions_module/main.tf

variable "composer_service_account" {
  description = "Service account email for Cloud Composer"
  type        = string
}

resource "google_project_iam_member" "composer_admin" {
  project = var.project_id
  role    = "roles/composer.admin"
  member  = "serviceAccount:${var.composer_service_account}"
}

resource "google_project_iam_member" "bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${var.composer_service_account}"
}

resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${var.composer_service_account}"
}

resource "google_project_iam_member" "secret_manager_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:terraform-admin-sa@lumley-analytics.iam.gserviceaccount.com"  # Update this to your Cloud Composer service account if different
}

resource "google_storage_bucket_iam_member" "object_storage_admin" {
  bucket = "us-east4-lumley-analytics-c-55c477d8-bucket"
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:terraform-admin-sa@lumley-analytics.iam.gserviceaccount.com"  # Update if a different service account is used
}

