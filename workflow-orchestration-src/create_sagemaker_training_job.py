import boto3
import os
sagemaker_boto3 = boto3.client('sagemaker')

def lambda_handler(event, context):
    """ Creates a SageMaker training job
    """

    BUCKET = event["BUCKET"]
    WORKFLOW_DATE_TIME = event["WORKFLOW_DATE_TIME"]
    PREFIX = "s3://{}/{}".format(BUCKET, WORKFLOW_DATE_TIME)

    TRAINING_DATA = "{}/data/train/train.csv".format(PREFIX)
    VALIDATION_DATA = "{}/data/validation/validation.csv".format(PREFIX)
    SOURCE_CODE = "{}/{}".format(PREFIX, "source-code/sourcedir.tar.gz")
    
    ENTRY_POINT_SCRIPT = event['TRAINING_SCRIPT']
    TRAINING_IMAGE = event['TRAINING_IMAGE']
    ROLE_ARN = event['ROLE_ARN']
    OUTPUT_ARTIFACTS_PATH = 's3://{}/{}'.format(BUCKET, WORKFLOW_DATE_TIME + '/model-artifacts/')
    INSTANCE_TYPE = event['TRAINING_INSTANCE_TYPE']
    INSTANCE_COUNT = event['TRAINING_INSTANCE_COUNT']
    VOLUME_SIZE_GB = event['TRAINING_VOLUME_SIZE_GB']
    
    WORKFLOW_NAME = event["WORKFLOW_NAME"]
    TRAINING_JOB_NAME = "{}-{}".format(WORKFLOW_NAME, WORKFLOW_DATE_TIME)

    try:
        response = sagemaker_boto3.create_training_job(
            TrainingJobName=TRAINING_JOB_NAME,
            HyperParameters={
                'n_estimators': '300',
                'min_samples_leaf': '3',
                'sagemaker_program': ENTRY_POINT_SCRIPT,
                'sagemaker_submit_directory': SOURCE_CODE      
            },
            AlgorithmSpecification={
                'TrainingImage': TRAINING_IMAGE,
                'TrainingInputMode': 'File',
                'MetricDefinitions': [
                    {'Name': 'median-AE', 'Regex': 'AE-at-50th-percentile: ([0-9.]+).*$'},
                ]
            },
            RoleArn=ROLE_ARN,
            InputDataConfig=[
                {
                    'ChannelName': 'train',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': TRAINING_DATA,
                            'S3DataDistributionType': 'FullyReplicated',
                        }
                    }
                },
                {
                    'ChannelName': 'validation',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': VALIDATION_DATA,
                            'S3DataDistributionType': 'FullyReplicated',
                        }
                    }
                },
            ],
            OutputDataConfig={'S3OutputPath': OUTPUT_ARTIFACTS_PATH},
            ResourceConfig={
                'InstanceType': INSTANCE_TYPE,
                'InstanceCount': INSTANCE_COUNT,
                'VolumeSizeInGB': VOLUME_SIZE_GB
            },
            StoppingCondition={'MaxRuntimeInSeconds': 86400},
            EnableNetworkIsolation=False
        )
        print(response)
    except Exception as e:
        print(e)
        print('Unable to create model.')
        raise(e)
    
    return response