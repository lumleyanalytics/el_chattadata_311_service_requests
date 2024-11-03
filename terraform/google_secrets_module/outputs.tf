output "secret_ids" {
  description = "List of Secret Manager secret IDs"
  value       = [for s in google_secret_manager_secret.secrets : s.id]
}
