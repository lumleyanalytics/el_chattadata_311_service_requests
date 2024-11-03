import os
import requests
import pandas as pd
from google.cloud import storage
from dotenv import load_dotenv
from typing import Optional, Dict, Callable
from flask import Request

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

# Function to upload DataFrame to GCS
def upload_to_gcs(df: pd.DataFrame, bucket_name: str, file_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    print(f"Data uploaded to GCS bucket {bucket_name} as {file_name}")

# Custom cleaning function for description field
def clean_description_field(df: pd.DataFrame) -> pd.DataFrame:
    if 'description' in df.columns:
        df['description'] = df['description'].apply(lambda x: f'"{x}"' if x and '\\' in str(x) else x)
    return df

# Main function for Cloud Function
def fetch_to_gcs(request: Request):
    request_json = request.get_json(silent=True)
    
    # Extract parameters from the request JSON
    api_url = request_json.get('api_url')
    gcs_bucket = request_json.get('gcs_bucket')
    gcs_file_name = request_json.get('gcs_file_name')
    api_key = request_json.get('api_key', os.getenv("API_KEY"))
    test_mode = request_json.get('test_mode', False)

    # Fetch data from API
    df = fetch_api_data(api_url=api_url, api_key=api_key, test_mode=test_mode)
    
    # Clean data if needed
    df = clean_description_field(df)
    
    # Upload DataFrame to GCS
    upload_to_gcs(df, gcs_bucket, gcs_file_name)

    return f"Data uploaded to {gcs_bucket} as {gcs_file_name}", 200
