{
    "DeliveryStreamDescription": {
        "DeliveryStreamName": "ED-Event-Stream",
        "DeliveryStreamARN": "arn:aws:firehose:eu-west-2:294382260790:deliverystream/ED-Event-Stream",
        "DeliveryStreamStatus": "ACTIVE",
        "DeliveryStreamEncryptionConfiguration": {
            "Status": "DISABLED"
        },
        "DeliveryStreamType": "DirectPut",
        "VersionId": "2",
        "CreateTimestamp": "2026-02-07T06:46:49.112000+00:00",
        "LastUpdateTimestamp": "2026-02-07T07:26:30.197000+00:00",
        "Destinations": [
            {
                "DestinationId": "destinationId-000000000001",
                "S3DestinationDescription": {
                    "RoleARN": "arn:aws:iam::294382260790:role/service-role/KinesisFirehoseServiceRole-ED-Event-Stre-eu-west-2-1770446245245",
                    "BucketARN": "arn:aws:s3:::ed-streaming",
                    "Prefix": "firehose/ed-stream/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
                    "ErrorOutputPrefix": "firehose/ed-stream/errors/",
                    "BufferingHints": {
                        "SizeInMBs": 1,
                        "IntervalInSeconds": 10
                    },
                    "CompressionFormat": "UNCOMPRESSED",
                    "EncryptionConfiguration": {
                        "NoEncryptionConfig": "NoEncryption"
                    },
                    "CloudWatchLoggingOptions": {
                        "Enabled": true,
                        "LogGroupName": "/aws/kinesisfirehose/ED-Event-Stream",
                        "LogStreamName": "DestinationDelivery"
                    }
                },
                "ExtendedS3DestinationDescription": {
                    "RoleARN": "arn:aws:iam::294382260790:role/service-role/KinesisFirehoseServiceRole-ED-Event-Stre-eu-west-2-1770446245245",
                    "BucketARN": "arn:aws:s3:::ed-streaming",
                    "Prefix": "firehose/ed-stream/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/",
                    "ErrorOutputPrefix": "firehose/ed-stream/errors/",
                    "BufferingHints": {
                        "SizeInMBs": 1,
                        "IntervalInSeconds": 10
                    },
                    "CompressionFormat": "UNCOMPRESSED",
                    "EncryptionConfiguration": {
                        "NoEncryptionConfig": "NoEncryption"
                    },
                    "CloudWatchLoggingOptions": {
                        "Enabled": true,
                        "LogGroupName": "/aws/kinesisfirehose/ED-Event-Stream",
                        "LogStreamName": "DestinationDelivery"
                    },
                    "ProcessingConfiguration": {
                        "Enabled": true,
                        "Processors": [
                            {
                                "Type": "AppendDelimiterToRecord",
                                "Parameters": []
                            }
                        ]
                    },
                    "S3BackupMode": "Disabled",
                    "DataFormatConversionConfiguration": {
                        "Enabled": false
                    },
                    "FileExtension": "",
                    "CustomTimeZone": "UTC"
                }
            }
        ],
        "HasMoreDestinations": false
    }
}

