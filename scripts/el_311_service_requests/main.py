import requests
import os
from google.cloud import secretmanager
from google.cloud import storage
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env (useful for local testing)
load_dotenv()

app = Flask(__name__)

# Replace with your actual GCP Project ID or use an environment variable
PROJECT_ID = "162045639883"

# Initialize Secret Manager Client
secret_client = secretmanager.SecretManagerServiceClient()

def get_secret(secret_id):
    """Fetch a secret from Google Secret Manager."""
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def trigger_cloud_function(url, payload=None):
    """Trigger a Cloud Function with an HTTP request."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GCP_IDENTITY_TOKEN')}"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_to_gcs():
    """Trigger the fetch_to_gcs Cloud Function."""
    return trigger_cloud_function(
        url=os.getenv("FETCH_TO_GCS_URL"),
        payload={
            "api_url": "https://www.chattadata.org/resource/8qb9-5fja.json",
            "gcs_bucket": "lumley_analytics_seeds",
            "gcs_file_name": "data/chattadata_311_service_requests.csv",
            "api_key": get_secret("CHATTADATA_API_KEY"),
            "test_mode": True
        }
    )

def gcs_to_bigquery():
    """Trigger the gcs_to_bigquery Cloud Function."""
    return trigger_cloud_function(
        url=os.getenv("GCS_TO_BIGQUERY_URL"),
        payload={
            "gcs_bucket": "lumley_analytics_seeds",
            "gcs_file_name": "data/chattadata_311_service_requests.csv",
            "bq_project_id": "lumley-analytics",
            "bq_dataset_id": "chatt_311_service_requests",
            "bq_table_id": "src_chattadata_311_service_requests",
            "write_disposition": "WRITE_TRUNCATE"
        }
    )

def gcs_to_snowflake():
    """Trigger the gcs_to_snowflake Cloud Function."""
    return trigger_cloud_function(
        url=os.getenv("GCS_TO_SNOWFLAKE_URL"),
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

@app.route("/", methods=["POST"])
def main():
    """Entry point for the Cloud Function."""
    try:
        # Execute tasks sequentially
        fetch_to_gcs()
        gcs_to_bigquery()
        gcs_to_snowflake()
        return jsonify({"status": "success", "message": "Data processed successfully."}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # For local testing only
    app.run(debug=True)
