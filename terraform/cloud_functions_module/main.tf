# cloud_functions_module/main.tf

resource "google_cloudfunctions_function" "el_311_service_requests" {
  name        = "${var.function_prefix}-el_311_service_requests"
  runtime     = "python310"
  entry_point = "main"
  region      = var.region

  available_memory_mb   = 1024
  timeout               = 540

  source_archive_bucket = var.gcs_bucket_name
  source_archive_object = "el_311_service_requests.zip"

  trigger_http = true

}
