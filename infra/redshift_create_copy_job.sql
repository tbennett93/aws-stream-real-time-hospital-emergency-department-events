copy staging.ed
from 's3://ed-streaming/glue/converted_parquet/'
iam_role 'arn:aws:iam::294382260790:role/service-role/AmazonRedshift-CommandsAccessRole-20260222T123146'
format as parquet
JOB CREATE ingest_ed_parquet
AUTO ON