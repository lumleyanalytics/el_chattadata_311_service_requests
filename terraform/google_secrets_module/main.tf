# google_secrets_module/main.tf

resource "google_secret_manager_secret" "secrets" {
  for_each  = var.secrets
  secret_id = each.key
  project   = var.project_id

  # Replication configuration
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secrets_version" {
  for_each    = var.secrets
  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value
}
