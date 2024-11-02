import os
import pandas as pd
from google.cloud import storage
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv
import argparse

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

def main():
    parser = argparse.ArgumentParser(description="Load data from GCS to Snowflake.")
    parser.add_argument('--gcs_bucket', required=True, help="GCS bucket name where the file is stored")
    parser.add_argument('--gcs_file_name', required=True, help="File name in GCS")
    parser.add_argument('--sf_user', default=os.getenv("SNOWFLAKE_USER"), help="Snowflake user")
    parser.add_argument('--sf_password', default=os.getenv("SNOWFLAKE_PASSWORD"), help="Snowflake password")
    parser.add_argument('--sf_account', default=os.getenv("SNOWFLAKE_ACCOUNT"), help="Snowflake account identifier")
    parser.add_argument('--sf_warehouse', required=True, help="Snowflake warehouse name")
    parser.add_argument('--sf_database', required=True, help="Snowflake database name")
    parser.add_argument('--sf_schema', required=True, help="Snowflake schema name")
    parser.add_argument('--sf_table', required=True, help="Snowflake table name")

    args = parser.parse_args()

    # Download data from GCS
    df = download_from_gcs(args.gcs_bucket, args.gcs_file_name)
    
    # Upload data to Snowflake
    upload_to_snowflake(
        df, 
        user=args.sf_user, 
        password=args.sf_password, 
        account=args.sf_account, 
        warehouse=args.sf_warehouse, 
        database=args.sf_database, 
        schema=args.sf_schema, 
        table=args.sf_table
    )

if __name__ == "__main__":
    main()