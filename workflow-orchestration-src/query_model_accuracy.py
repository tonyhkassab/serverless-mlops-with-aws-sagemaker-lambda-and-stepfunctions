import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sm_client = boto3.client('sagemaker')

#Retrieve transform job name from event and return transform job status.
def lambda_handler(event, context):
    JOB_NAME = "{}-{}".format(event["WORKFLOW_NAME"], event["WORKFLOW_DATE_TIME"])

    try:
        response = sm_client.describe_training_job(TrainingJobName=JOB_NAME)
        logger.info("Training job:{} has status:{}.".format(JOB_NAME,
            response['TrainingJobStatus']))

    except Exception as e:
        response = ('Failed to read training status!'+ 
                    ' The training job may not exist or the job name may be incorrect.'+ 
                    ' Check SageMaker to confirm the job name.')
        print(e)
        print('{} Attempted to read job name: {}.'.format(response, JOB_NAME))

    #We can't marshall datetime objects in JSON response. So convert
    #all datetime objects returned to unix time.
    for index, metric in enumerate(response['FinalMetricDataList']):
        metric['Timestamp'] = metric['Timestamp'].timestamp()

    return {
        'statusCode': 200,
        'trainingMetrics': response['FinalMetricDataList']
    }