# bigquery_module/main.tf

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bigquery_dataset_id
  project    = var.project_id
  location   = var.region
}

resource "google_bigquery_table" "table" {
  project  = var.project_id
  dataset_id = var.bigquery_dataset_id
  table_id = var.bigquery_table_id
}