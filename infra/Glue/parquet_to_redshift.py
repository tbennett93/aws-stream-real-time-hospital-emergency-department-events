import boto3


redshift = boto3.client('redshift-data')

files_location = 's3://ed-streaming/glue/converted_parquet/'
iam_role = 'arn:aws:iam::294382260790:role/service-role/AmazonRedshift-CommandsAccessRole-20260222T123146'

SQL = f"""copy staging.ed
from '{files_location}'
iam_role '{iam_role}'
format as parquet"""

response = redshift.execute_statement(
    Sql=SQL,
    Database='dev',
    WithEvent=False,
    StatementName='copy_s3_parquet_to_redshift',
    WorkgroupName='hospital-data-workgroup',
    SessionKeepAliveSeconds=20
)


