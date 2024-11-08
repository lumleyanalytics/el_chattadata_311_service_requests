import os
import argparse
import pandas as pd
from google.cloud import storage, bigquery
from dotenv import load_dotenv
from io import StringIO
from flask import Request
import logging

# Load environment variables from .env if they exist
load_dotenv()

def download_from_gcs(bucket_name: str, file_name: str) -> pd.DataFrame:
    """Download a CSV file from GCS and return it as a DataFrame."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download CSV data and read into DataFrame
    data = blob.download_as_text()
    df = pd.read_csv(StringIO(data))  # Use StringIO for compatibility with pd.read_csv
    logging.info(f"Downloaded data from GCS bucket {bucket_name}, file {file_name}")
    return df

def upload_to_bigquery(df: pd.DataFrame, project_id: str, dataset_id: str, table_id: str, write_disposition: str = "WRITE_TRUNCATE"):
    """Upload a DataFrame to BigQuery, treating all columns as STRING to retain column names."""
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    # Define schema with all columns as STRING
    schema = [bigquery.SchemaField(col, "STRING") for col in df.columns]

    # Configure load job with schema
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=write_disposition,
        skip_leading_rows=1,  # Skip the header row if DataFrame includes column names
        source_format=bigquery.SourceFormat.CSV
    )

    # Load data to BigQuery
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for the job to complete
    logging.info(f"Data loaded into BigQuery table {table_ref} with disposition {write_disposition}")

def main(request: Request):
    # Parse JSON payload from the request
    request_json = request.get_json(silent=True)
    if not request_json:
        logging.error("Invalid or missing JSON payload")
        return "Invalid or missing JSON payload", 400

    # Retrieve parameters from the request JSON
    gcs_bucket = request_json.get('gcs_bucket')
    gcs_file_name = request_json.get('gcs_file_name')
    bq_project_id = request_json.get('bq_project_id')
    bq_dataset_id = request_json.get('bq_dataset_id')
    bq_table_id = request_json.get('bq_table_id')
    write_disposition = request_json.get('write_disposition', 'WRITE_TRUNCATE')

    # Validate required parameters
    if not all([gcs_bucket, gcs_file_name, bq_project_id, bq_dataset_id, bq_table_id]):
        logging.error("Missing required parameters in JSON payload")
        return "Missing required parameters in JSON payload", 400

    # Download data from GCS
    try:
        df = download_from_gcs(gcs_bucket, gcs_file_name)
    except Exception as e:
        logging.error(f"Error downloading data from GCS: {e}")
        return f"Error downloading data from GCS: {e}", 500

    # Upload data to BigQuery
    try:
        upload_to_bigquery(df, bq_project_id, bq_dataset_id, bq_table_id, write_disposition)
    except Exception as e:
        logging.error(f"Error uploading data to BigQuery: {e}")
        return f"Error uploading data to BigQuery: {e}", 500

    return "Data successfully transferred from GCS to BigQuery", 200
