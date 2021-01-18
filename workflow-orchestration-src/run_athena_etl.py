import boto3
athena = boto3.client('athena')

MY_QUERY = """
SELECT
    features.*
    ,labels.f1m_gv
FROM
    "octank"."octank_offline_feature_store" features
JOIN
    "octank"."octank_labels" labels
ON
    features.tconst = labels.tconst AND
    features.season = labels.season
"""


def lambda_handler(event, context):
    BUCKET = event["BUCKET"]
    WORKFLOW_DATE_TIME = event["WORKFLOW_DATE_TIME"]
    OUTPUT = "s3://{}/{}/data/etl".format(BUCKET, WORKFLOW_DATE_TIME)

    queryStart = athena.start_query_execution(
        QueryExecutionContext = {
            'Database': 'octank'
        },
        QueryString = MY_QUERY,
        ResultConfiguration = {"OutputLocation": OUTPUT}
    )
    return {"QueryExecutionId": queryStart["QueryExecutionId"]}