# cloud_functions_module/outputs.tf

output "fetch_to_gcs_url" {
  value = google_cloudfunctions_function.fetch_to_gcs.https_trigger_url
}

output "gcs_to_bigquery_url" {
  value = google_cloudfunctions_function.gcs_to_bigquery.https_trigger_url
}

output "gcs_to_snowflake_url" {
  value = google_cloudfunctions_function.gcs_to_snowflake.https_trigger_url
}
