import boto3
import os
import mimetypes
import tarfile
import io

def lambda_handler(event, context):
    """ Pulls AWS Glue and SageMaker source code from CodeCommit and writes it to S3.
    This funciton creates a tarball of the SageMaker scripts before sending to S3 since
    SageMaker training jobs expect code to be in a tarball on S3.
    """
    # target bucket
    bucket = boto3.resource('s3').Bucket(event['BUCKET'])
    output_prefix = "{}/{}".format(event["WORKFLOW_DATE_TIME"], "source-code")
    
    # source codecommit
    codecommit = boto3.client('codecommit', region_name=event['REGION'])
    repository_name = event['REPO']
    branch = event['BRANCH']
    ml_dir = event["ML_DIR"]
    data_processing_dir = event["DATA_PROCESSING_DIR"]

    # First create a tar ball with sagemaker scripts to S3 with name source.dir.tar.gz
    buf = io.BytesIO()
    with tarfile.open('sourcedir', mode="w:gz", fileobj=buf) as tar:
        # Reads each file in the branch and uploads it to the s3 bucket
        for blob in get_blob_list(codecommit, repository_name, branch, ml_dir):
            path = blob['path']
            blobId = blob['blobId']
            content = (codecommit.get_blob(repositoryName=repository_name, blobId=blobId))['content']
            tarinfo = tarfile.TarInfo(path)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
    # close tar file
    tarobject = buf.getvalue()
    # put tar ball in s3
    s3BucketKey = '{}/{}'.format(output_prefix, 'sourcedir.tar.gz')
    bucket.put_object(Body=(tarobject), Key=s3BucketKey)

    
    # Sagemaker Processing.
    for blob in get_blob_list(codecommit, repository_name, branch, data_processing_dir):
        path = blob['path']
        blobId=blob['blobId']
        content = (codecommit.get_blob(repositoryName=repository_name, blobId=blobId))['content']
        s3BucketKey = '{}/{}'.format(output_prefix, path)
        bucket.put_object(Body=(content), Key=s3BucketKey)
    return('SUCCESS')            


def get_blob_list(codecommit, repository, branch, path):
    """ Returns a list of a all files in a CodeCommit branch
    """
    response = codecommit.get_differences(
            repositoryName=repository,
            afterCommitSpecifier=branch,
            afterPath=path
            )

    blob_list = [difference['afterBlob'] for difference in response['differences']]
    while 'nextToken' in response:
        response = codecommit.get_differences(
                repositoryName=repository,
                afterCommitSpecifier=branch,
                nextToken=response['nextToken']
                )
        blob_list += [difference['afterBlob'] for difference in response['differences']]

    return blob_list    
