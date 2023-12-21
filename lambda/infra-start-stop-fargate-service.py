import boto3
import json

def lambda_handler(event, context):
    ecs = boto3.client('ecs')
    cluster_name = 'fargate-cluster'
    service_name = 'ab3-chat-demo-loadbalancer'

    action = event.get('action')
    desired_count = 1 if action == 'start' else 0

    response = ecs.update_service(
        cluster=cluster_name,
        service=service_name,
        desiredCount=desired_count
    )

    # Extract necessary information
    return_message = {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
        'message': 'Service updated successfully' if response['ResponseMetadata']['HTTPStatusCode'] == 200 else 'Failed to update service'
    }

    return {
        'statusCode': 200,
        'body': json.dumps(return_message)
    }
