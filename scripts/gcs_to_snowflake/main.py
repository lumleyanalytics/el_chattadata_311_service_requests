import os
import pandas as pd
from google.cloud import storage
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv
from flask import Request

# Load environment variables
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

def upload_to_snowflake(df: pd.DataFrame, user: str, password: str, account: str, warehouse: str, database: str, schema: str, table: str):
    """Upload a DataFrame to Snowflake, creating the table with all VARCHAR(16777216) columns."""
    
    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    # Convert column names to uppercase for Snowflake compatibility
    df.columns = [col.upper() for col in df.columns]

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    cursor = conn.cursor()

    # Generate CREATE TABLE statement with all VARCHAR(16777216) columns
    column_definitions = [f"{column} VARCHAR" for column in df.columns]
    create_table_query = f"""
    CREATE OR REPLACE TABLE {schema}.{table} (
        {', '.join(column_definitions)}
    );
    """
    cursor.execute(create_table_query)
    print(f"Created or replaced table {schema}.{table} with all columns as VARCHAR(16777216).")

    # Write data to Snowflake in bulk with write_pandas
    success, nchunks, nrows, _ = write_pandas(conn, df, table_name=table, schema=schema)
    
    if success:
        print(f"Successfully loaded {nrows} rows into {schema}.{table} in Snowflake.")
    else:
        print("Data load to Snowflake failed.")

    # Close the connection
    conn.close()

def main(request: Request):
    # Retrieve parameters from environment variables
    gcs_bucket = os.getenv('GCS_BUCKET')
    gcs_file_name = os.getenv('GCS_FILE_NAME')
    sf_user = os.getenv("SNOWFLAKE_USER")
    sf_password = os.getenv("SNOWFLAKE_PASSWORD")
    sf_account = os.getenv("SNOWFLAKE_ACCOUNT")
    sf_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    sf_database = os.getenv("SNOWFLAKE_DATABASE")
    sf_schema = os.getenv("SNOWFLAKE_SCHEMA")
    sf_table = os.getenv("SNOWFLAKE_TABLE")

    # Download data from GCS
    df = download_from_gcs(gcs_bucket, gcs_file_name)
    
    # Upload data to Snowflake
    upload_to_snowflake(
        df, 
        user=sf_user, 
        password=sf_password, 
        account=sf_account, 
        warehouse=sf_warehouse, 
        database=sf_database, 
        schema=sf_schema, 
        table=sf_table
    )
    
    return "Data successfully transferred from GCS to Snowflake", 200
