response = client.create_transform_job(
    TransformJobName = '...',
    ModelName = '<SageMaker Model Name>',
    TransformInput = {
        'DataSource': {
            'S3DataSource': {
                'S3DataType': 'S3Prefix',
                'S3Uri': 's3://...'
            }
        },
        'ContentType': 'text/csv',
        'CompressionType': 'None',
        'SplitType': 'Line'
    },
    TransformOutput = {
        'S3OutputPath': 's3://...',
        'KmsKeyId': ''
    },
    TransformResources = {
        'InstanceType': 'ml.m5.large', 'InstanceCount': 1
    },
    ...
)