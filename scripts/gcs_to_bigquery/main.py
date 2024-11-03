# gcs_to_bigquery.py
import os
import pandas as pd
from google.cloud import storage, bigquery
from dotenv import load_dotenv
from io import StringIO
from flask import Request

# Load environment variables from .env if they exist
load_dotenv()

def download_from_gcs(bucket_name: str, file_name: str) -> pd.DataFrame:
    """Download a CSV file from GCS and return it as a DataFrame."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download CSV data and read into DataFrame
    data = blob.download_as_text()
    df = pd.read_csv(StringIO(data))  # Use StringIO from the standard library
    print(f"Downloaded data from GCS bucket {bucket_name}, file {file_name}")
    return df

def upload_to_bigquery(df: pd.DataFrame, project_id: str, dataset_id: str, table_id: str, write_disposition: str = "WRITE_TRUNCATE"):
    """Upload a DataFrame to BigQuery."""
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    # Configure load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,  # Overwrite or append
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV
    )

    # Load data to BigQuery
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for the job to complete
    print(f"Data loaded into BigQuery table {table_ref} with disposition {write_disposition}")

def main(request: Request):
    # Retrieve parameters from environment variables
    gcs_bucket = os.getenv('GCS_BUCKET')
    gcs_file_name = os.getenv('GCS_FILE_NAME')
    bq_project_id = os.getenv('BQ_PROJECT_ID')
    bq_dataset_id = os.getenv('BQ_DATASET_ID')
    bq_table_id = os.getenv('BQ_TABLE_ID')
    write_disposition = os.getenv('WRITE_DISPOSITION', 'WRITE_TRUNCATE')

    # Download data from GCS
    df = download_from_gcs(gcs_bucket, gcs_file_name)
    
    # Upload data to BigQuery
    upload_to_bigquery(df, bq_project_id, bq_dataset_id, bq_table_id, write_disposition)
    
    return "Data successfully transferred from GCS to BigQuery", 200
