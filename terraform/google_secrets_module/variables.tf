variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "secrets" {
  description = "A map of secret names and values"
  type        = map(string)
}

# google_secrets_module/variables.tf
variable "chattadata_api_key" {
  description = "API Key for Chattadata"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake user"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
}

variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
}

