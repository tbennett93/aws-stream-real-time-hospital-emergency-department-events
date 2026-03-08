import pandas as pd
import datetime
from pathlib import Path
import pyarrow
import boto3





def get_new_files(s3, bucket: str):
    #get new firehose files
    # prefix = f"firehose/ed-stream/new/{partition_key}" #limits to just todays files
    prefix = f"firehose/ed-stream/raw/"

    list_files_response: dict = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )

    if "Contents" not in list_files_response.keys():
        raise ValueError(f"No files in {bucket}/{prefix} or prefix does not exist")
        
        
    filepaths = [f"s3://ed-streaming/{content['Key']}" for content in list_files_response["Contents"] ]
    
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ed-streaming-raw-processing-manifest")
    
    unprocessed_files = []
    for filepath in filepaths:
        resp = table.get_item(
            Key={"filepath": filepath}
        )
        
        if "Item" not in resp:
            unprocessed_files.append(filepath)

    return unprocessed_files


def build_df(files: list):
    
    #build dfs
    df_combined = pd.concat([pd.read_json(file, lines=True) for file in files])
            
    if df_combined.empty:
        raise ValueError("No data found, please investigate")
    
    return df_combined


def validate_df(df_combined: pd.DataFrame, schema: dict):
    
    for col, dtype in schema.items():
        if dtype == "datetime":
            df_combined[col] = pd.to_datetime(df_combined[col],errors='coerce') #cannot be properly parsed using astype
        else:
            df_combined[col] = df_combined[col].astype(dtype)

    #produce clean and dirty dataframes - hold bad data in quarantine for reprocessing
    quarantine_mask = df_combined[list(schema.keys())].isna().any(axis='columns')
    df_quarantine = df_combined[quarantine_mask].copy()
    df_clean = df_combined[~quarantine_mask].copy()

    if df_clean.empty:
        raise ValueError("No valid data found, please investigate")
            
    return df_clean, df_quarantine



def build_output_path(base: Path, partition_key: str, timestamp: datetime):
    output_path = base
    output_path = output_path / partition_key / f"ed_{timestamp}.parquet"
    return output_path.as_posix()


def output_parquet_to_s3(
        s3, 
        df_clean: pd.DataFrame, 
        df_quarantine:pd.DataFrame, 
        bucket: str, 
        output_path_clean: str,
        output_path_dirty: str
        ):
    
    parquet_clean = df_clean.to_parquet( index=False)

    #output clean
    s3.put_object(
        Bucket = bucket,
        Body = parquet_clean,
        Key = output_path_clean
    )

    #output quarantine
    if not df_quarantine.empty:
        parquet_quarantine = df_quarantine.to_parquet( index=False)

        s3.put_object(
            Bucket = bucket,
            Body = parquet_quarantine,
            Key = output_path_dirty

        )



def get_key_from_uri(uri: str, bucket: str):
    return uri.replace(f"s3://{bucket}/","")

#move files from processed to prevent reprocessing
def copy_files_to_processed(s3, files: list, bucket: str, destination_path: str):
    for file in files:
        file = get_key_from_uri(file, bucket)
        filename = file.split("/")[-1] 
        s3.copy_object(
            Bucket=bucket,
            Key=f"{destination_path}{filename}",
            CopySource={"Bucket": bucket, "Key": file}
        )

#delete original files
def delete_original_files(s3, files: list, bucket: str):
    for file in files:
        file = get_key_from_uri(file, bucket)
        s3.delete_object(
            Bucket=bucket,
            Key=file
        )
        

#log processed file so it isnt reingested
def write_manifest_records(files: list):

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ed-streaming-raw-processing-manifest")

    for file in files:
        table.put_item(
            Item={
                "filepath": file
            }
        )


#process start
if __name__ == '__main__':

    s3 = boto3.client('s3')
    bucket = "ed-streaming"

    date=datetime.date.today()
    year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
    partition_key = f"year={year}/month={month}/day={day}/"

    #get files
    files = get_new_files(s3, bucket)
    if len(files)==0:
        raise ValueError("No new files to process")
    
    #build df
    df_combined = build_df(files)

    #validation
    schema={
        "event_id":"str",
        "attendance_id":"str",
        "patient_id":"str",
        "event_type":"str",
        "event_ts":"datetime",
        "recorded_ts":"datetime",
        "source_system":"str",
        "patient_name":"str"

    }
    df_clean, df_quarantine = validate_df(df_combined, schema)


    timestamp = datetime.datetime.now()

    #Build output paths
    base_clean = Path("glue/converted_parquet/")
    output_path_clean = build_output_path(base_clean, partition_key, timestamp)

    base_dirty = Path("glue/quarantine/converted_parquet/")
    output_path_dirty = build_output_path(base_dirty, partition_key, timestamp)

    #output to s3
    output_parquet_to_s3(
        s3, 
        df_clean=df_clean, 
        df_quarantine=df_quarantine, 
        bucket = bucket,
        output_path_clean=output_path_clean, 
        output_path_dirty=output_path_dirty
    )
    
    #record completion to prevent duplicate loads
    write_manifest_records(files)


    #move input files to processed
    #copy_files_to_processed(s3, files, bucket, f"firehose/ed-stream/processed/{partition_key}")
    #delete_original_files(s3, files, bucket ) # no longer deletes original files as this breaks idempotency. Instead ingestion is managed by partition
