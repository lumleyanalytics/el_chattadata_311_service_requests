# terraform_service_account_module/main.tf

resource "google_service_account" "terraform_sa" {
  account_id   = "terraform-admin-sa"
  display_name = "Terraform Admin Service Account"
  project = "lumley-analytics"
}

resource "google_service_account_key" "terraform_sa_key" {
  service_account_id = google_service_account.terraform_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

output "terraform_sa_email" {
  value = google_service_account.terraform_sa.email
}

output "service_account_key" {
  value     = google_service_account_key.terraform_sa_key.private_key
  sensitive = true
}
