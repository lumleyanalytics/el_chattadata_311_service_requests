from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import get_current_context
from airflow.utils.dates import days_ago
import os

# Set default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

# Define the DAG
with DAG(
    'chattanooga_311_service_requests_data_pipeline',
    default_args=default_args,
    description='A DAG to process and load Chattanooga 311 data to BigQuery and Snowflake',
    schedule_interval=None,  # Set to None or change to desired interval
    start_date=days_ago(1),
    catchup=False,
) as dag:

    @task
    def fetch_to_gcs():
        """Task to fetch data from API and upload to GCS."""
        os.system('/opt/homebrew/bin/python3.10 "/Users/apratsunrthd/Documents/Python Data Training/fetch_to_gcs.py" '
                  '--api_url "https://www.chattadata.org/resource/8qb9-5fja.json" '
                  '--gcs_bucket "lumley_analytics_seeds" '
                  '--gcs_file_name "data/api_data_test_20241102.csv" '
                  '--test_mode')

    @task
    def gcs_to_bigquery():
        """Task to load data from GCS to BigQuery."""
        os.system('/opt/homebrew/bin/python3.10 "/Users/apratsunrthd/Documents/Python Data Training/gcs_to_bigquery.py" '
                  '--gcs_bucket "lumley_analytics_seeds" '
                  '--gcs_file_name "data/api_data_test_20241102.csv" '
                  '--bq_project_id "lumley-analytics" '
                  '--bq_dataset_id "chatt_311_service_requests" '
                  '--bq_table_id "tst_311_requests" '
                  '--write_disposition "WRITE_TRUNCATE"')

    @task
    def gcs_to_snowflake():
        """Task to load data from GCS to Snowflake."""
        os.system('/opt/homebrew/bin/python3.10 "/Users/apratsunrthd/Documents/Python Data Training/gcs_to_snowflake.py" '
                  '--gcs_bucket "lumley_analytics_seeds" '
                  '--gcs_file_name "data/api_data_test_20241102.csv" '
                  '--sf_warehouse "COMPUTE_WH" '
                  '--sf_database "CHATTADATA_311_SERVICE_REQUESTS" '
                  '--sf_schema "PUBLIC" '
                  '--sf_table "TST_311_SERVICE_REQUESTS"')

    # Define task dependencies
    fetch_task = fetch_to_gcs()
    bigquery_task = gcs_to_bigquery()
    snowflake_task = gcs_to_snowflake()

    fetch_task >> [bigquery_task, snowflake_task]
