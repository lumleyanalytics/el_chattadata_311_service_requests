resource "google_cloud_scheduler_job" "fetch_data_job" {
  name     = "fetch-data-job"
  schedule = "0 0 * * *" # Adjust to desired frequency (daily at midnight)

  http_target {
    uri        = google_cloud_run_service.fetch_data_service.status.url
    http_method = "POST"
    oidc_token {
      service_account_email = var.scheduler_service_account_email # Service account for auth
    }
  }

  time_zone = "America/New_York" # Adjust to preferred time zone
}
