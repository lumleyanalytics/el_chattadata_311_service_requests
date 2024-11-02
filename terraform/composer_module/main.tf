# main.tf

# Create Composer Environment
resource "google_composer_environment" "composer" {
  name    = var.environment_name
  project = var.project_id
  region  = var.region

  config {
    software_config {
      image_version = "composer-2.9.9-airflow-2.9.3"
    }
  }
}

