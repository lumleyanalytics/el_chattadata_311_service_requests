variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "secrets" {
  description = "A map of secret names and values"
  type        = map(string)
}
