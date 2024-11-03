import os
import logging
from google.cloud import secretmanager
from fetch_to_gcs import fetch_api_data, upload_to_gcs, clean_description_field
from gcs_to_bigquery import download_from_gcs as download_from_gcs_to_bq, upload_to_bigquery
from gcs_to_snowflake import gcs_to_snowflake

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to get a secret from Secret Manager
def get_secret(secret_id):
    project_id = "162045639883"
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Main function to orchestrate each step
def main(request: Request):
    request_json = request.get_json(silent=True)  # Accept and ignore JSON payload if present
    
    # Define constants and parameters
    api_url = "https://www.chattadata.org/resource/8qb9-5fja.json"
    gcs_bucket = "lumley_analytics_seeds"
    gcs_file_name = "data/chattadata_311_service_requests.csv"
    api_key = get_secret("CHATTADATA_API_KEY")
    
    bq_project_id = "lumley-analytics"
    bq_dataset_id = "chatt_311_service_requests"
    bq_table_id = "src_chattadata_311_service_requests"
    
    sf_user = get_secret("SNOWFLAKE_USER")
    sf_password = get_secret("SNOWFLAKE_PASSWORD")
    sf_account = get_secret("SNOWFLAKE_ACCOUNT")
    sf_warehouse = "COMPUTE_WH"
    sf_database = "CHATTADATA_311_SERVICE_REQUESTS"
    sf_schema = "PUBLIC"
    sf_table = "SRC_CHATTADATA_311_SERVICE_REQUESTS"

    # Track whether it's the first batch to enable truncation
    first_batch = True
    
    # Process batches of data
    for batch_df in fetch_api_data(api_url=api_url, api_key=api_key):
        try:
            # Step 1: Upload to BigQuery
            upload_to_bigquery(
                batch_df, 
                project_id=bq_project_id, 
                dataset_id=bq_dataset_id, 
                table_id=bq_table_id, 
                truncate=first_batch
            )
            logging.info(f"Batch uploaded to BigQuery table {bq_table_id}")
        
            # Step 2: Upload to Snowflake
            upload_to_snowflake(
                batch_df,
                user=sf_user,
                password=sf_password,
                account=sf_account,
                warehouse=sf_warehouse,
                database=sf_database,
                schema=sf_schema,
                table=sf_table,
                truncate=first_batch
            )
            logging.info(f"Batch uploaded to Snowflake table {sf_table}")

            # Only truncate on the first batch
            first_batch = False

        except Exception as e:
            logging.error(f"Error during batch processing: {e}")
            return f"Error during batch processing: {e}", 500

    return "Data processing completed successfully.", 200
