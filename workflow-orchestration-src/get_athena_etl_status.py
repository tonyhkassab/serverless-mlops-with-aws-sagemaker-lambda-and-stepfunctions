import boto3
athena = boto3.client('athena')

def lambda_handler(event, context):
    QueryExecutionId = event["QueryExecutionId"]
    
    queryExecution = athena.get_query_execution(QueryExecutionId=QueryExecutionId)
    
    return {"ETLJobStatus": queryExecution["QueryExecution"]["Status"]["State"]}

