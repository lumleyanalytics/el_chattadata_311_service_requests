from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from google.cloud import secretmanager
import requests
import os

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

# Instantiate the DAG
with DAG(
    "trigger_cloud_functions_dag",
    default_args=default_args,
    description="A DAG to trigger Cloud Functions with secrets from Secret Manager",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
) as dag:

    from google.cloud import secretmanager

    def get_secret(secret_id):
        project_id = "lumley-analytics"  # Replace with your actual project ID or fetch from environment variables
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")


    def trigger_cloud_function(url, payload=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('GCP_IDENTITY_TOKEN')}"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    @task(task_id="fetch_to_gcs")
    def fetch_to_gcs():
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

    @task(task_id="gcs_to_bigquery")
    def gcs_to_bigquery():
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

    @task(task_id="gcs_to_snowflake")
    def gcs_to_snowflake():
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

    # Define task dependencies
    fetch_to_gcs() >> [gcs_to_bigquery(), gcs_to_snowflake()]
