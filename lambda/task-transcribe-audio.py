import boto3
import urllib.parse
import json

def lambda_handler(event, context):
    # Initialize the Transcribe and S3 clients
    transcribe = boto3.client('transcribe')
    s3 = boto3.client('s3')

    # Get the bucket name and file key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    # Construct the file URI
    file_uri = f"s3://{bucket}/{key}"
    
    # Setting up the Transcribe job name
    job_name = key.replace("/", "-").replace(".mp3", "")
    
    # Starting the Transcribe job
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': file_uri},
            MediaFormat='mp3',
            LanguageCode='en-US',
            OutputBucketName=bucket,
            OutputKey=f"text-transcripts/{job_name}.json"
        )
        print(f"Started transcription job: {job_name}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Started transcription job: {job_name}")
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps("Error starting transcription job")
        }
