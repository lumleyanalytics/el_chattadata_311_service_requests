import os
import pandas as pd
import requests
from google.cloud import storage
from flask import Flask

app = Flask(__name__)

# Function to fetch API data
def fetch_api_data(api_url: str, api_key: str = None, batch_limit: int = 1000) -> pd.DataFrame:
    offset = 0
    all_data = []
    headers = {"X-App-Token": api_key} if api_key else {}

    while True:
        params = {"$limit": batch_limit, "$offset": offset}
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Request failed at offset {offset}")
            break

        batch_data = response.json()
        if not batch_data:
            break

        all_data.extend(batch_data)
        offset += batch_limit
        print("Retrieved", offset, "records")

    return pd.DataFrame(all_data)

# Function to upload data to GCS
def upload_to_gcs(df: pd.DataFrame, bucket_name: str, file_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    print(f"Data uploaded to GCS bucket {bucket_name} as {file_name}")

@app.route('/fetch-data', methods=['POST'])
def fetch_and_store_data():
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")
    gcs_bucket = os.getenv("GCS_BUCKET")
    gcs_file_name = os.getenv("GCS_FILE_NAME")

    # Fetch data
    df = fetch_api_data(api_url=api_url, api_key=api_key)

    # Upload data to GCS
    upload_to_gcs(df, gcs_bucket, gcs_file_name)
    return "Data fetched and stored in GCS.", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
