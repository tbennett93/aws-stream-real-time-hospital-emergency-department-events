from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.docker.operators.docker import DockerOperator

from docker.types import Mount


from datetime import timedelta
from datetime import datetime
from airflow.hooks.base import BaseHook

with DAG(
    dag_id="process_ed",
    start_date=datetime(2024,1,1),
    schedule=timedelta(minutes=15) ,
    catchup=False,
    default_args={
        "retries": 2,
        "aws_conn_id":"aws_default",
        "wait_for_completion":True,
        "region_name":"eu-west-2"        
    },

):

    wait_for_file = S3KeySensor(
        task_id="wait_for_file",
        bucket_name="ed-streaming",
        bucket_key="firehose/ed-stream/raw/*",
        wildcard_match=True,
        aws_conn_id="aws_default",
        poke_interval=10,
        timeout=600,
    )

    convert_to_parquet_glue = GlueJobOperator(
        task_id="convert_to_parquet",
        job_name="ed-streaming-data-convert-json-to-parquet"   # already created in AWS
  
    )

    copy_parquet_to_redshift_glue = GlueJobOperator(
        task_id="copy_parquet_to_redshift",
        job_name="ed-streaming-move-parquet-to-redshift"   # already created in AWS

    )



    aws_conn = BaseHook.get_connection("aws_default")




    dbt_run = DockerOperator(
        task_id="dbt_build",
        image="your-dbt:latest",
        command="build",
        working_dir="/app",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source="C:\\Users\\tbenn\\.dbt",
                target="/root/.dbt",
                type="bind"
            )
        ],
        environment={
            "AWS_ACCESS_KEY_ID": aws_conn.login,
            "AWS_SECRET_ACCESS_KEY": aws_conn.password,
            "AWS_DEFAULT_REGION": "eu-west-2",
        }
    )

    convert_to_parquet_glue >> copy_parquet_to_redshift_glue >> dbt_run


#wait for file
#trigger glue job to move file
#trigger glue job to process file into redshift
#trigger dbt to process redshift ELT