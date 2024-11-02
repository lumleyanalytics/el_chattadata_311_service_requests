# gcs_module/main.tf

resource "google_storage_bucket" "bucket" {
  name     = var.bucket_name
  location = var.region
  project  = var.project_id
}
