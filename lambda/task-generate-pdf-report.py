import boto3
import json

def lambda_handler(event, context):
    ecs = boto3.client('ecs')
    cluster_name = 'fargate-cluster'
    task_definition = 'ab3-background-pdf-gen'

    action = event.get('action')

    if action == 'start':
        response = ecs.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        'YOUR SUBNETS'
                    ],
                    'securityGroups': [
                        'YOUR SGS',  
                    ],
                    # To set to PRIVATE, ensure your VPC has private connectivity to Container Registry, if ECS retrieves container from there
                    # More info: https://repost.aws/questions/QU3mcDN5ZHT_Sga3AbyczO2w/lambda-function-cannot-run-ecs-task-unable-to-retrieve-ecr-registry-auth
                    'assignPublicIp': 'ENABLED'
                }
            },
        )
        message = 'Task started successfully'
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid action'})
        }

    return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
        'body': json.dumps({'message': message})
    }
