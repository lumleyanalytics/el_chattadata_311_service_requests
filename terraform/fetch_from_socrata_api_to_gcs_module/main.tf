provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Step 1: Create a GCS Bucket for storing data
resource "google_storage_bucket" "data_bucket" {
  name                        = var.gcs_bucket
  location                    = var.region
  project                     = var.project_id

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}

# Step 2: Create an Artifact Registry repository for Cloud Run images
resource "google_artifact_registry_repository" "cloud_run_repo" {
  provider      = google-beta
  project       = var.project_id
  location      = var.region
  repository_id = "cloud-run-fetch-store"
  format        = "DOCKER"
  description   = "Artifact Registry for Cloud Run fetch-and-store service"
}

# Step 3: Create a Cloud Run service for fetching data
resource "google_cloud_run_service" "fetch_service" {
  name     = "fetch-from-api"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/fetch-data-to-gcs:latest" # Ensure this matches your build image
        env {
          name  = "API_URL"
          value = var.api_url
        }
        env {
          name  = "GCS_BUCKET"
          value = var.gcs_bucket
        }
      }
    }
  }
  autogenerate_revision_name = true

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Step 4: Create a Service Account for the Cloud Run service
resource "google_service_account" "fetch_service_account" {
  account_id   = "fetch-service-account"
  display_name = "Fetch Service Account"
  project      = var.project_id
}

# Step 5: Grant invoker role to the service account
resource "google_project_iam_member" "fetch_service_account_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.fetch_service_account.email}"
}

# Step 6: Grant public access to the Cloud Run service (optional)
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_service.fetch_service.location
  project  = google_cloud_run_service.fetch_service.project
  service  = google_cloud_run_service.fetch_service.name
  role     = "roles/run.invoker"
  member   = "allUsers" # Use this cautiously; adjust as needed
}

# Step 7: Create a Cloud Scheduler job to trigger the Cloud Run service
resource "google_cloud_scheduler_job" "fetch_job" {
  name     = "fetch-job"
  schedule = "*/10 * * * *" # Every 10 minutes, adjust as needed
  project  = var.project_id
  region   = var.region

  http_target {
    uri        = google_cloud_run_service.fetch_service.status[0].url
    http_method = "POST"
    oauth_token {
      service_account_email = google_service_account.fetch_service_account.email
    }
  }
}
