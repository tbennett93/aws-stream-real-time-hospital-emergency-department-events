import json
import boto3
from generate_new_event import new_event


def send_to_firehose(event):
    event = json.dumps(event).encode('utf-8') #convert dict to bytes for firehose
    firehose = boto3.client('firehose')
    response = firehose.put_record(    
        DeliveryStreamName='ED-Event-Stream',
        Record={
            'Data': event
        }
    )

    return response