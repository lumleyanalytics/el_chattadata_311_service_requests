# fetch_to_gcs.py
import os
import requests
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv
from typing import Optional, Dict, Callable
import argparse

# Load environment variables from .env if they exist
load_dotenv()

# Function to fetch API data
def fetch_api_data(
    api_url: str,
    api_key: Optional[str] = None,
    params: Optional[Dict] = None,
    batch_limit: int = 1000,
    test_mode: bool = False
) -> pd.DataFrame:
    offset = 0
    all_data = []
    headers = {"X-App-Token": api_key} if api_key else {}

    while True:
        batch_params = params.copy() if params else {}
        batch_params.update({"$limit": batch_limit, "$offset": offset})
        
        response = requests.get(api_url, headers=headers, params=batch_params)
        if response.status_code != 200:
            print(f"Request failed at offset {offset}")
            break

        batch_data = response.json()
        if not batch_data:
            break

        all_data.extend(batch_data)
        offset += batch_limit
        print("Retrieved", offset, "records")

        if test_mode:
            break

    return pd.DataFrame(all_data)

def upload_to_gcs(df: pd.DataFrame, bucket_name: str, file_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    print(f"Data uploaded to GCS bucket {bucket_name} as {file_name}")

def clean_data(df: pd.DataFrame, cleaning_func: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None) -> pd.DataFrame:
    if cleaning_func:
        df = cleaning_func(df)
    return df

# Custom cleaning function for description field
def clean_description_field(df: pd.DataFrame) -> pd.DataFrame:
    if 'description' in df.columns:
        df['description'] = df['description'].apply(lambda x: f'"{x}"' if x and '\\' in str(x) else x)
    return df

def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="Fetch data from API and upload to GCS.")
    parser.add_argument('--api_url', required=True, help="API URL to fetch data from")
    parser.add_argument('--gcs_bucket', required=True, help="GCS bucket name")
    parser.add_argument('--gcs_file_name', required=True, help="File name/path in GCS")
    parser.add_argument('--api_key', help="API key for accessing the API", default=os.getenv("API_KEY"))
    parser.add_argument('--test_mode', action='store_true', help="Fetch only one batch for testing")
    
    args = parser.parse_args()
    
    # Fetch data from API
    df = fetch_api_data(api_url=args.api_url, api_key=args.api_key, test_mode=args.test_mode)
    
    # Clean data if needed
    df = clean_data(df, clean_description_field)
    
    # Upload DataFrame to GCS
    upload_to_gcs(df, args.gcs_bucket, args.gcs_file_name)

if __name__ == "__main__":
    main()
