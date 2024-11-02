# gcs_to_bigquery.py
import os
import argparse
import pandas as pd
from google.cloud import storage, bigquery
from dotenv import load_dotenv

# Load environment variables from .env if they exist
load_dotenv()

def download_from_gcs(bucket_name: str, file_name: str) -> pd.DataFrame:
    """Download a CSV file from GCS and return it as a DataFrame."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download CSV data and read into DataFrame
    data = blob.download_as_text()
    df = pd.read_csv(pd.io.common.StringIO(data))
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

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Load data from GCS to BigQuery.")
    parser.add_argument('--gcs_bucket', required=True, help="GCS bucket name where the file is stored")
    parser.add_argument('--gcs_file_name', required=True, help="File name in GCS")
    parser.add_argument('--bq_project_id', required=True, help="BigQuery project ID")
    parser.add_argument('--bq_dataset_id', required=True, help="BigQuery dataset ID")
    parser.add_argument('--bq_table_id', required=True, help="BigQuery table ID")
    parser.add_argument('--write_disposition', default="WRITE_TRUNCATE", choices=["WRITE_TRUNCATE", "WRITE_APPEND"], help="Write mode for BigQuery: overwrite or append")

    args = parser.parse_args()

    # Download data from GCS
    df = download_from_gcs(args.gcs_bucket, args.gcs_file_name)
    
    # Upload data to BigQuery
    upload_to_bigquery(df, args.bq_project_id, args.bq_dataset_id, args.bq_table_id, args.write_disposition)

if __name__ == "__main__":
    main()
