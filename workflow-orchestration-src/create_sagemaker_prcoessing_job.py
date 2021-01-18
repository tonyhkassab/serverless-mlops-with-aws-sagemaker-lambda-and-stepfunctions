import boto3
sagemaker_boto3 = boto3.client('sagemaker')

def lambda_handler(event, context):
    BUCKET = event["BUCKET"]
    WORKFLOW_DATE_TIME = event["WORKFLOW_DATE_TIME"]
    JOB_NAME = "{}-{}".format(event["WORKFLOW_NAME"], WORKFLOW_DATE_TIME)

    DATA_SOURCE = event["DATA_SOURCE"]
    SOURCE_CODE_PREFIX = "{}/source-code".format(WORKFLOW_DATE_TIME)
    PROCESSING_SCRIPT = event["PROCESSING_SCRIPT"]
    
    # Output data paths
    TRAIN_PATH = 's3://{}/{}/data/train'.format(BUCKET, WORKFLOW_DATE_TIME)
    VALID_PATH = 's3://{}/{}/data/validation'.format(BUCKET, WORKFLOW_DATE_TIME)
    TEST_PATH = 's3://{}/{}/data/test'.format(BUCKET, WORKFLOW_DATE_TIME)

    response = sagemaker_boto3.create_processing_job(
        ProcessingJobName = JOB_NAME,
        ProcessingInputs = [
            {'InputName': 'input-1',
             'S3Input': {'S3Uri': DATA_SOURCE,
                         'LocalPath': '/opt/ml/processing/input',
                         'S3DataType': 'S3Prefix',
                         'S3InputMode': 'File',
                         'S3DataDistributionType': 'ShardedByS3Key',
                         'S3CompressionType': 'None'
                        }
            },
            {'InputName': 'code',
             'S3Input': {'S3Uri': "s3://{}/{}/{}".format(BUCKET, SOURCE_CODE_PREFIX, PROCESSING_SCRIPT),
                         'LocalPath': '/opt/ml/processing/input/code',
                         'S3DataType': 'S3Prefix',
                         'S3InputMode': 'File',
                         'S3DataDistributionType': 'FullyReplicated',
                         'S3CompressionType': 'None'
                        }
            }
        ],
        ProcessingOutputConfig = {
            'Outputs': [{'OutputName': 'train',
                         'S3Output': {'S3Uri': TRAIN_PATH,
                                      'LocalPath': '/opt/ml/processing/train',
                                      'S3UploadMode': 'EndOfJob'
                                     }
                        },
                        {'OutputName': 'valid',
                         'S3Output': {'S3Uri': VALID_PATH,
                                      'LocalPath': '/opt/ml/processing/validation',
                                      'S3UploadMode': 'EndOfJob'
                                     }
                        },
                        {'OutputName': 'test',
                         'S3Output': {'S3Uri': TEST_PATH,
                                      'LocalPath': '/opt/ml/processing/test',
                                      'S3UploadMode': 'EndOfJob'
                                     }
                        }]
        },
        ProcessingResources = {'ClusterConfig': {'InstanceCount': event["PROCESSING_INSTANCE_COUNT"],
                                                 'InstanceType': event["PROCESSING_INSTANCE_TYPE"],
                                                 'VolumeSizeInGB': event["PROCESSING_VOLUME_SIZE_GB"]
                                                }
                              },
        StoppingCondition = {'MaxRuntimeInSeconds': 86400},
        AppSpecification = {'ImageUri': event["PROCESSING_IMAGE"],
                            'ContainerArguments':  ['--train-test-split-ratio', '0.2'], 
                            'ContainerEntrypoint': ['python3', 
                                                    '/opt/ml/processing/input/code/'+ event["PROCESSING_SCRIPT"]
                                                   ]
                           },
        RoleArn = event["ROLE_ARN"]
    )
    return event
    