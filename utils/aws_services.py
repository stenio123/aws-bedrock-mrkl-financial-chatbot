import boto3
import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local development
load_dotenv()

def get_bedrock_client():
    # Check if the AWS_PROFILE environment variable is set
    if 'AWS_PROFILE' in os.environ:
        # Use profile-based authentication for local development
        boto3.setup_default_session(profile_name=os.getenv('AWS_PROFILE'))
    
    # If AWS_PROFILE is not set, boto3 will automatically use IAM role credentials in AWS environments
    bedrock = boto3.client('bedrock-runtime')
    return bedrock

def get_cognito_client():
    # Check if the AWS_PROFILE environment variable is set
    if 'AWS_PROFILE' in os.environ:
        # Use profile-based authentication for local development
        boto3.setup_default_session(profile_name=os.getenv('AWS_PROFILE'))
    
    # If AWS_PROFILE is not set, boto3 will automatically use IAM role credentials in AWS environments
    bedrock = boto3.client('cognito')
    return bedrock

def get_kendra_client():
    # Check if the AWS_PROFILE environment variable is set
    if 'AWS_PROFILE' in os.environ:
        # Use profile-based authentication for local development
        boto3.setup_default_session(profile_name=os.getenv('AWS_PROFILE'))
    
    # If AWS_PROFILE is not set, boto3 will automatically use IAM role credentials in AWS environments
    bedrock = boto3.client('kendra')
    return bedrock

#TODO fix so it works inside Docker container
def get_kendra_index():
    return os.getenv('KENDRA_INDEX')

def get_s3_client():
    # Check if the AWS_PROFILE environment variable is set
    if 'AWS_PROFILE' in os.environ:
        # Use profile-based authentication for local development
        boto3.setup_default_session(profile_name=os.getenv('AWS_PROFILE'))
    
    # If AWS_PROFILE is not set, boto3 will automatically use IAM role credentials in AWS environments
    s3_client = boto3.client('s3')
    return s3_client

def get_s3_bucket():
    if 'AWS_S3_BUCKET' in os.environ:
        return(os.getenv('AWS_S3_BUCKET'))
