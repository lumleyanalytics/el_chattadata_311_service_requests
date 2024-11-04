# permissions_module/main.tf

resource "google_project_iam_member" "secret_manager_access_terraform" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:terraform-admin-sa@lumley-analytics.iam.gserviceaccount.com"  # Update this to your Cloud Composer service account if different
}

resource "google_project_iam_member" "secret_manager_access_lumley_analytics" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:lumley-analytics@appspot.gserviceaccount.com"  # Update this to your Cloud Composer service account if different
}

resource "google_project_iam_member" "cloud_function_invoker_lumley_analytics" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:lumley-analytics@appspot.gserviceaccount.com"  # Update this to your Cloud Composer service account if different
}

resource "google_storage_bucket_iam_member" "object_storage_admin" {
  bucket = "us-east4-lumley-analytics-c-55c477d8-bucket"
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:terraform-admin-sa@lumley-analytics.iam.gserviceaccount.com"  # Update if a different service account is used
}

# Grant Cloud Run Invoker role to the Scheduler service account
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  location    = google_cloud_run_service.fetch_data_service.location
  project     = google_cloud_run_service.fetch_data_service.project
  service     = google_cloud_run_service.fetch_data_service.name
  role        = "roles/run.invoker"
  member      = "serviceAccount:${module.service_accounts.scheduler_sa.email}"  # Make sure this matches your service account
}

