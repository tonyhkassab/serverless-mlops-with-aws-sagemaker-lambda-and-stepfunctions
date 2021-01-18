import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sm_client = boto3.client('sagemaker')

def lambda_handler(event, context):
    JOB_NAME = "{}-{}".format(event["WORKFLOW_NAME"], event["WORKFLOW_DATE_TIME"])

    try:
        response = sm_client.describe_processing_job(ProcessingJobName=JOB_NAME)
        logger.info("Processing job:{} has status:{}.".format(JOB_NAME,
            response['ProcessingJobStatus']))

    except Exception as e:
        response = ('Failed to read processing status!'+ 
                    ' The processing job may not exist or the job name may be incorrect.')
        print(e)
        print('{} Attempted to read job name: {}.'.format(response, JOB_NAME))


    return {
        'statusCode': 200,
        'ProcessingJobStatus': response['ProcessingJobStatus']
    }