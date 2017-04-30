import os
import boto3
import config

s3client = boto3.client(
    's3',
    aws_access_key_id=config.awskeyid,
    aws_secret_access_key=config.awskey,
    region_name='us-west-2'
)

s3resource = boto3.resource(
    's3',
    aws_access_key_id=config.awskeyid,
    aws_secret_access_key=config.awskey,
    region_name='us-west-2'
)

os.chdir(os.path.join('Z:', 'LVG', 'sc-batch3'))
files = os.listdir(os.curdir)

for f in files:
    print f
    data = open(f, 'rb')
    s3resource.Bucket('stlvg-stage3').put_object(Key=f, Body=data)
