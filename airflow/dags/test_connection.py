from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from datetime import datetime

with DAG(
    dag_id="test_aws_connection",
    start_date=datetime(2024,1,1),
    schedule=None,
    catchup=False,
):

    list_files = S3ListOperator(
        task_id="list_s3_bucket",
        bucket="ed-streaming",
        aws_conn_id="aws_default"
    )