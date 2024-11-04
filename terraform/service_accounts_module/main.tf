# Scheduler Service Account
resource "google_service_account" "scheduler_sa" {
  account_id   = "scheduler-sa"
  display_name = "Scheduler Service Account"
}

