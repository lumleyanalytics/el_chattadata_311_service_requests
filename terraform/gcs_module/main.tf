# gcs_module/main.tf

resource "google_storage_bucket" "bucket" {
  name     = var.bucket_name
  location = var.region
  project  = var.project_id

  # Enable versioning for rollback or change tracking
  versioning {
    enabled = true
  }

  # Optional: Set public access prevention to keep the bucket private
  uniform_bucket_level_access = true
}

# Output the bucket name to use in other modules
output "bucket_name" {
  value = google_storage_bucket.bucket.name
}
