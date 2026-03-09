import boto3
import datetime
import json





def get_prefix():
    date=datetime.date.today()
    year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
    partition_key = f"year={year}/month={month}/day={day}/"
    return f'glue/converted_parquet/{partition_key}' #todays files



def get_s3_files(bucket, prefix, s3):
    list_files_response: dict = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )

    if "Contents" not in list_files_response.keys():
        raise ValueError(f"No files in {bucket}/{prefix} or prefix does not exist")


    return [f"s3://ed-streaming/{content['Key']}" for content in list_files_response["Contents"] ]


def get_unprocessed_files(filepaths, manifest_table):
    unprocessed_files = []
    for filepath in filepaths:
        resp = manifest_table.get_item(
            Key={"filepath": filepath}
        )
        
        if "Item" not in resp:
            unprocessed_files.append(filepath)

    return unprocessed_files

def write_manifest_file(bucket, manifest_file_key, unprocessed_files, s3):
    #populate a manifest file with unprocessed files. Files are added to manifest when processing
    manifest_entries = []
    for x in unprocessed_files:

        key = x.replace(f"s3://{bucket}/", "")

        obj = s3.head_object(Bucket=bucket, Key=key)

        manifest_entry = {
            "url": x,
            "meta": {
                "content_length": obj["ContentLength"]
            }
        }
        manifest_entries.append(manifest_entry)

    manifest_dic = {}
    manifest_dic.setdefault("entries", manifest_entries)


    #write  manifest file defining the files for redshift to process
    manifest_bytes = json.dumps(manifest_dic).encode("utf-8")

    s3.put_object(
        Bucket=bucket,
        Key=manifest_file_key,
        Body=manifest_bytes
    )




def copy_to_redshift(bucket, manifest_file_key, iam_role, database, schema, table, workgroup, redshift):
#copy data to redshift. use manifest to avoid re-processing files
    
    SQL = f"""copy "{schema}".{table}
    from 's3://{bucket}/{manifest_file_key}'
    iam_role '{iam_role}'
    format as parquet
    MANIFEST
    """

    return redshift.execute_statement(
        Sql=SQL,
        Database=database,
        WithEvent=False,
        StatementName='copy_s3_parquet_to_redshift',
        WorkgroupName=workgroup,
        SessionKeepAliveSeconds=20
    )


def update_manifest_store_with_processed_files(files: list, table ):
    for file in files:
        table.put_item(
            Item={
                "filepath": file
            }
        )


#Start

prefix = get_prefix()

s3 = boto3.client('s3')
bucket = "ed-streaming"
filepaths = get_s3_files(bucket, prefix, s3)

dynamodb = boto3.resource("dynamodb")
manifest_table = dynamodb.Table("ed-streaming-warehouse-load-manifest")

unprocessed_files = get_unprocessed_files(filepaths, manifest_table)

manifest_file_key = "redshift/unprocessed.manifest"
write_manifest_file(bucket, manifest_file_key, unprocessed_files, s3)

redshift = boto3.client('redshift-data')
iam_role = 'arn:aws:iam::294382260790:role/service-role/AmazonRedshift-CommandsAccessRole-20260222T123146'
database = 'dev'
table_name = 'ed'
schema = 'raw'
workgroup = 'hospital-data-workgroup'
copy_to_redshift(bucket, manifest_file_key, iam_role, database, schema, table_name, workgroup, redshift)

update_manifest_store_with_processed_files(unprocessed_files, manifest_table)


# import time

# statement_id = response["Id"]

# while True:
#    result = redshift.describe_statement(Id=statement_id)
#    print("status", result["Status"])

#    if result["Status"] in ["FAILED", "FINISHED", "ABORTED"]:
#        print("final result:", result)
#        break

#    time.sleep(2)
