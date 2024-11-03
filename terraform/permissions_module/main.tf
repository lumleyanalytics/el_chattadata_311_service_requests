# permissions_module/main.tf

resource "google_project_iam_member" "secret_manager_access_terraform" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:terraform-admin-sa@lumley-analytics.iam.gserviceaccount.com"  # Update this to your Cloud Composer service account if different
}

resource "google_storage_bucket_iam_member" "object_storage_admin" {
  bucket = "us-east4-lumley-analytics-c-55c477d8-bucket"
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:terraform-admin-sa@lumley-analytics.iam.gserviceaccount.com"  # Update if a different service account is used
}



