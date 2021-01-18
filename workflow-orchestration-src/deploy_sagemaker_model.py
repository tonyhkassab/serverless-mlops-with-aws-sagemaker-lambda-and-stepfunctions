import boto3
import os

sagemaker_boto3 = boto3.client('sagemaker')

def lambda_handler(event, context):
    """ Creates a SageMaker model and either
    updates or creates an endpoint
    """
    BUCKET = event["BUCKET"]
    WORKFLOW_NAME = event["WORKFLOW_NAME"]
    WORKFLOW_DATE_TIME = event["WORKFLOW_DATE_TIME"]

    prefix = "s3://{}/{}".format(BUCKET, WORKFLOW_DATE_TIME)
    name = "{}-{}".format(WORKFLOW_NAME, WORKFLOW_DATE_TIME)
    endpoint = WORKFLOW_NAME
    container = event['SERVING_IMAGE']
    
            
    #model_prefix = "{}/{}".format(prefix, "model-artifacts")
    #model_suffix = "{}-{}/{}".format(WORKFLOW_NAME, WORKFLOW_DATE_TIME, "output/model.tar.gz")
    #model_data_url = "{}/{}".format(model_prefix, model_suffix)

    model_data_url = sagemaker_boto3.describe_training_job(TrainingJobName=name)['ModelArtifacts']['S3ModelArtifacts']

    
    event["SOURCE_CODE_DIR"] = "{}/{}".format(prefix, "source-code/sourcedir.tar.gz")

    
    print('Creating model resource from training artifact...')
    create_model(name, container, model_data_url, event)
    
    print('Creating endpoint configuration...')
    create_endpoint_config(name, event)
    
    print('Checking if model endpoint already exists...')
    if check_endpoint_exists(endpoint):
        print('Existing endpoint found for model. Updating existing model endpoint...')
        update_endpoint(endpoint, name)
    else:
        print('There is no existing endpoint for this model. Creating new model endpoint...')
        create_endpoint(endpoint, name)
    event['stage'] = 'Deployment'
    event['status'] = 'Creating'
    event['message'] = 'Started deploying model "{}" to endpoint "{}"'.format(name, endpoint)
    return event



def create_model(name, container, model_data_url, env_params):
    """ Create SageMaker model.
    Args:
        name (string): Name to label model with
        container (string): Registry path of the Docker image that contains the model algorithm
        model_data_url (string): URL of the model artifacts created during training to download to container
    Returns:
        (None)
    """
    try:
        sagemaker_boto3.create_model(
            ModelName=name,
            PrimaryContainer={
                'Image': container,
                'ModelDataUrl': model_data_url,
                'Environment':{
                    "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
                    "SAGEMAKER_PROGRAM": env_params['SERVING_SCRIPT'],
                    "SAGEMAKER_SUBMIT_DIRECTORY": env_params['SOURCE_CODE_DIR'],
                    "SAGEMAKER_REGION": env_params['REGION'],
                    "SAGEMAKER_ENABLE_CLOUDWATCH_METRICS": "false"
                }
            },
            ExecutionRoleArn=env_params['ROLE_ARN']
        )
    except Exception as e:
        print(e)
        print('Unable to create model.')
        raise(e)



def create_endpoint_config(name, env_params):
    """ Create SageMaker endpoint configuration. 
    Args:
        name (string): Name to label endpoint configuration with.
    Returns:
        (None)
    """
    try:
        sagemaker_boto3.create_endpoint_config(
            EndpointConfigName=name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',                    
                    'ModelName': name,
                    'InitialInstanceCount': env_params['SERVING_INSTANCE_COUNT'],
                    'InstanceType': env_params['SERVING_INSTANCE_TYPE']
                }
            ]
        )
    except Exception as e:
        print(e)
        print('Unable to create endpoint configuration.')
        raise(e)



def check_endpoint_exists(endpoint_name):
    """ Check if SageMaker endpoint for model already exists.
    Args:
        endpoint_name (string): Name of endpoint to check if exists.
    Returns:
        (boolean)
        True if endpoint already exists.
        False otherwise.
    """
    try:
        sagemaker_boto3.describe_endpoint(
            EndpointName=endpoint_name
        )
        return True
    except Exception as e:
        return False



def create_endpoint(endpoint_name, config_name):
    """ Create SageMaker endpoint with input endpoint configuration.
    Args:
        endpoint_name (string): Name of endpoint to create.
        config_name (string): Name of endpoint configuration to create endpoint with.
    Returns:
        (None)
    """
    try:
        sagemaker_boto3.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
    except Exception as e:
        print(e)
        print('Unable to create endpoint.')
        raise(e)



def update_endpoint(endpoint_name, config_name):
    """ Update SageMaker endpoint to input endpoint configuration. 
    Args:
        endpoint_name (string): Name of endpoint to update.
        config_name (string): Name of endpoint configuration to update endpoint with.
    Returns:
        (None)
    """
    try:
        sagemaker_boto3.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
    except Exception as e:
        print(e)
        print('Unable to update endpoint.')
        raise(e)