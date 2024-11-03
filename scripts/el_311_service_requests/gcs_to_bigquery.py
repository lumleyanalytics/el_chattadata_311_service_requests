import os
import pandas as pd
from google.cloud import storage, bigquery
from dotenv import load_dotenv
from io import StringIO
import logging
from typing import Optional

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

def gcs_to_bigquery(
    gcs_bucket: str,
    gcs_file_name: str,
    bq_project_id: str,
    bq_dataset_id: str,
    bq_table_id: str,
    write_disposition: Optional[str] = "WRITE_TRUNCATE"
):
    # Download data from GCS
    try:
        df = download_from_gcs(gcs_bucket, gcs_file_name)
    except Exception as e:
        logging.error(f"Error downloading data from GCS: {e}")
        raise RuntimeError(f"Error downloading data from GCS: {e}")

    # Upload data to BigQuery
    try:
        upload_to_bigquery(df, bq_project_id, bq_dataset_id, bq_table_id, write_disposition)
    except Exception as e:
        logging.error(f"Error uploading data to BigQuery: {e}")
        raise RuntimeError(f"Error uploading data to BigQuery: {e}")

    return "Data successfully transferred from GCS to BigQuery"
