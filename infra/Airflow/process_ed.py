from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

from datetime import datetime, date

with DAG(
    dag_id="process_ed",
    start_date=datetime(2024,1,1),
    schedule=None,
    catchup=False,
):

    wait_for_file = S3KeySensor(
        task_id="wait_for_file",
        bucket_name="ed-streaming",
        bucket_key="firehose/ed-stream/new/*",
        wildcard_match=True,
        aws_conn_id="aws_default",
        poke_interval=10,
        timeout=600,
    )

    run_glue = GlueJobOperator(
        task_id="convert_to_parquet",
        job_name="ed-streaming-data-convert-json-to-parquet",   # already created in AWS
        aws_conn_id="aws_default",
        wait_for_completion=True,
        region_name="eu-west-2"
    )


    wait_for_file >> run_glue


#wait for file
#trigger glue job to move file
#trigger glue job to process file into redshift
#trigger dbt to process redshift ELT