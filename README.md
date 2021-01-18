# Serverless MLOps with AWS SageMaker, Lambda and StepFunctions
To run this demo, clone this repo to your SageMaker notebook instance, find the IAM role of your SageMaker notebook instance and attach CodeCommit, S3, Lambda and StepFunctions and IAM `full access policies` to it. 

Next, go through the following notebooks in order:
* `Lab0-Setup.ipynb`: Creates the required S3 Buckets, Docker Image and IAM Roles.
* `Lab1-SageMaker-SDK.ipynb`: Creates and runs SageMaker Processing, Training and Hosting jobs using the SageMaker SDK.
* `Lab2-Lambda-Setup.ipynb`: Migrates the SageMaker jobs to AWS Lambda.
* `Lab3-StepFunction-Setup.ipynb`: Orchestrates the entire workflow using an AWS StepFunction
* `Lab4-CleanUp.ipynb`: Delete demo resources

![Workflow Graph](/README-IMAGES/stepfunctions_graph.png)
