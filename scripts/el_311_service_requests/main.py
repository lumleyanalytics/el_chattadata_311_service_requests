import os
import requests
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import secretmanager
from flask import Request

# Function to get an identity token
def get_identity_token(audience):
    credentials, _ = default()
    auth_request = Request()
    credentials.refresh(auth_request)
    token = credentials.id_token_with_audience(audience)
    return token

# Function to get a secret from Secret Manager
def get_secret(secret_id):
    project_id = os.getenv("GCP_PROJECT_ID")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Function to trigger a Cloud Function with an identity token
def trigger_cloud_function(url, payload=None):
    token = get_identity_token(url)  # Get the identity token for the Cloud Function URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"  # Include the token in the Authorization header
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Main function to orchestrate function calls, handling a JSON payload
def main(request: Request):
    request_json = request.get_json(silent=True)  # Accept the JSON payload, ignoring if empty

    # URLs for each Cloud Function, obtained from environment variables
    fetch_to_gcs_url = os.getenv("FETCH_TO_GCS_URL")
    gcs_to_bigquery_url = os.getenv("GCS_TO_BIGQUERY_URL")
    gcs_to_snowflake_url = os.getenv("GCS_TO_SNOWFLAKE_URL")

    # Call each function
    try:
        # Fetch data to GCS
        fetch_response = trigger_cloud_function(
            fetch_to_gcs_url,
            payload={
                "api_url": "https://www.chattadata.org/resource/8qb9-5fja.json",
                "gcs_bucket": "lumley_analytics_seeds",
                "gcs_file_name": "data/chattadata_311_service_requests.csv",
                "api_key": get_secret("CHATTADATA_API_KEY"),
                "test_mode": True
            }
        )
        print("Fetch to GCS response:", fetch_response)

        # GCS to BigQuery
        bq_response = trigger_cloud_function(
            gcs_to_bigquery_url,
            payload={
                "gcs_bucket": "lumley_analytics_seeds",
                "gcs_file_name": "data/chattadata_311_service_requests.csv",
                "bq_project_id": "lumley-analytics",
                "bq_dataset_id": "chatt_311_service_requests",
                "bq_table_id": "src_chattadata_311_service_requests",
                "write_disposition": "WRITE_TRUNCATE"
            }
        )
        print("GCS to BigQuery response:", bq_response)

        # GCS to Snowflake
        snowflake_response = trigger_cloud_function(
            gcs_to_snowflake_url,
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
        print("GCS to Snowflake response:", snowflake_response)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Return a response indicating success
    return "Triggered all Cloud Functions successfully.", 200

