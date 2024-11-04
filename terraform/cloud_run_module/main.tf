resource "google_cloud_run_service" "fetch_data_service" {
  name     = "fetch-data-to-gcs"
  location = var.region
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/fetch-data-to-gcs:latest" # Update with your image location
        env {
          name  = "API_URL"
          value = var.api_url
        }
        env {
          name  = "API_KEY"
          value = var.api_key
        }
        env {
          name  = "GCS_BUCKET"
          value = var.gcs_bucket
        }
        env {
          name  = "GCS_FILE_NAME"
          value = var.gcs_file_name
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

# Allow unauthenticated access if desired, or grant specific roles
resource "google_cloud_run_service_iam_member" "invoker" {
  location    = google_cloud_run_service.fetch_data_service.location
  project     = google_cloud_run_service.fetch_data_service.project
  service     = google_cloud_run_service.fetch_data_service.name
  role        = "roles/run.invoker"
  member      = "allUsers" # or specify an identity if needed
}

resource "google_artifact_registry_repository" "cloud_run_repo" {
  provider      = google-beta
  project       = var.project_id
  location      = var.region
  repository_id = "cloud-run-fetch-store"
  format        = "DOCKER"
  description   = "Artifact Registry for Cloud Run fetch-and-store service"
}

resource "google_cloudbuild_trigger" "fetch_data_image_build" {
  name   = "fetch-data-image-build"
  project = var.project_id

  github {
    owner = var.github_repo_owner
    name  = var.github_repo_name
    push {
      branch = var.github_branch  # e.g., "main" or "master"
    }
  }

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "gcr.io/${var.project_id}/fetch-data-to-gcs:latest", "."]
    }
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${var.project_id}/fetch-data-to-gcs:latest"]
    }
    images = ["gcr.io/${var.project_id}/fetch-data-to-gcs:latest"]
  }
}


