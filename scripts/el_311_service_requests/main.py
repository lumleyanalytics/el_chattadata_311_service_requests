from flask import Request
from google.cloud import secretmanager
import requests
import os

def get_secret(secret_id):
    """Fetch secret from Secret Manager."""
    project_id = os.getenv("GCP_PROJECT_ID")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def trigger_cloud_function(url, payload=None):
    """Trigger a Cloud Function with the given URL and payload."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GCP_IDENTITY_TOKEN')}"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def main(request: Request):
    """Entrypoint for the Cloud Run Function, ignoring any incoming JSON payload."""
    try:
        # Fetch URLs from environment variables
        fetch_to_gcs_url = os.getenv("FETCH_TO_GCS_URL")
        gcs_to_bigquery_url = os.getenv("GCS_TO_BIGQUERY_URL")
        gcs_to_snowflake_url = os.getenv("GCS_TO_SNOWFLAKE_URL")

        # Call fetch_to_gcs
        fetch_to_gcs_response = trigger_cloud_function(
            url=fetch_to_gcs_url,
            payload={
                "api_url": "https://www.chattadata.org/resource/8qb9-5fja.json",
                "gcs_bucket": "lumley_analytics_seeds",
                "gcs_file_name": "data/chattadata_311_service_requests.csv",
                "api_key": get_secret("CHATTADATA_API_KEY"),
                "test_mode": True
            }
        )

        # Call gcs_to_bigquery and gcs_to_snowflake
        gcs_to_bigquery_response = trigger_cloud_function(
            url=gcs_to_bigquery_url,
            payload={
                "gcs_bucket": "lumley_analytics_seeds",
                "gcs_file_name": "data/chattadata_311_service_requests.csv",
                "bq_project_id": "lumley-analytics",
                "bq_dataset_id": "chatt_311_service_requests",
                "bq_table_id": "src_chattadata_311_service_requests",
                "write_disposition": "WRITE_TRUNCATE"
            }
        )

        gcs_to_snowflake_response = trigger_cloud_function(
            url=gcs_to_snowflake_url,
            payload={
                "gcs_bucket": "lumley_analytics_seeds",
                "gcs_file_name": "data/chattadata_311_service_requests.csv",
                "sf_user": get_secret("SNOWFLAKE_USER"),
                "sf_password": get_secret("SNOWFLAKE_PASSWORD"),
                "sf_account": get_secret("SNOWFLAKE_ACCOUNT"),
                "sf_warehouse": "COMPUTE_WH",
                "sf_database": "CHATTADATA_311_SERVICE_REQUESTS",
                "sf_schema": "PUBLIC",
                "sf_table": "SRC_CHATTADATA_311_SERVICE_REQUESTS"
            }
        )

        return {
            "fetch_to_gcs": fetch_to_gcs_response,
            "gcs_to_bigquery": gcs_to_bigquery_response,
            "gcs_to_snowflake": gcs_to_snowflake_response
        }, 200

    except Exception as e:
        return str(e), 500
