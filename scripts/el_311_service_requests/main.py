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
def main(request=None):
    if request:
        # Ignore any JSON payload if request is provided, handle it gracefully
        request_json = request.get_json(silent=True)  # Accept and ignore JSON payload if present

    # Step 1: Fetch data from API and upload to GCS
    try:
        api_url = "https://www.chattadata.org/resource/8qb9-5fja.json"
        gcs_bucket = "lumley_analytics_seeds"
        gcs_file_name = "data/chattadata_311_service_requests.csv"
        api_key = get_secret("CHATTADATA_API_KEY")
        
        # Fetch and clean data
        df = fetch_api_data(api_url=api_url, api_key=api_key, test_mode=True)
        df = clean_description_field(df)
        
        # Upload data to GCS
        upload_to_gcs(df, gcs_bucket, gcs_file_name)
        logging.info(f"Data successfully fetched and uploaded to {gcs_bucket}/{gcs_file_name}")
        
    except Exception as e:
        logging.error(f"Error during fetch-to-GCS step: {e}")
        return f"Error during fetch-to-GCS step: {e}", 500

    # Step 2: Transfer data from GCS to BigQuery
    try:
        bq_project_id = "lumley-analytics"
        bq_dataset_id = "chatt_311_service_requests"
        bq_table_id = "src_chattadata_311_service_requests"
        
        # Download from GCS and upload to BigQuery
        df_bq = download_from_gcs_to_bq(gcs_bucket, gcs_file_name)
        upload_to_bigquery(df_bq, bq_project_id, bq_dataset_id, bq_table_id)
        logging.info(f"Data successfully uploaded to BigQuery table {bq_table_id}")
        
    except Exception as e:
        logging.error(f"Error during GCS-to-BigQuery step: {e}")
        return f"Error during GCS-to-BigQuery step: {e}", 500

    # Step 3: Transfer data from GCS to Snowflake
    try:
        sf_user = get_secret("SNOWFLAKE_USER")
        sf_password = get_secret("SNOWFLAKE_PASSWORD")
        sf_account = get_secret("SNOWFLAKE_ACCOUNT")
        
        sf_warehouse = "COMPUTE_WH"
        sf_database = "CHATTADATA_311_SERVICE_REQUESTS"
        sf_schema = "PUBLIC"
        sf_table = "SRC_CHATTADATA_311_SERVICE_REQUESTS"
        
        # Execute GCS to Snowflake transfer
        gcs_to_snowflake(
            gcs_bucket=gcs_bucket,
            gcs_file_name=gcs_file_name,
            sf_user=sf_user,
            sf_password=sf_password,
            sf_account=sf_account,
            sf_warehouse=sf_warehouse,
            sf_database=sf_database,
            sf_schema=sf_schema,
            sf_table=sf_table
        )
        logging.info(f"Data successfully uploaded to Snowflake table {sf_table}")
        
    except Exception as e:
        logging.error(f"Error during GCS-to-Snowflake step: {e}")
        return f"Error during GCS-to-Snowflake step: {e}", 500

    # Final response indicating success
    return "Data processing completed successfully.", 200
