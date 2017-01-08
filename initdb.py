import os
import re
import arrow
import boto3
import simplejson as json
import time
import config
from botocore.exceptions import ClientError
import random

dbclient = boto3.client(
    'dynamodb',
    aws_access_key_id=config.awskeyid,
    aws_secret_access_key=config.awskey,
    region_name='us-west-2'
)
dbresource = boto3.resource(
    'dynamodb',
    aws_access_key_id=config.awskeyid,
    aws_secret_access_key=config.awskey,
    region_name='us-west-2'
)

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


def getWorkBuckets():
    bucketList = []
    allBuckets = s3client.list_buckets()
    for bucket in allBuckets['Buckets']:
        try:
            tags = s3client.get_bucket_tagging(Bucket=bucket['Name'])
        except ClientError:
            continue
        for ts in tags['TagSet']:
            if ts['Key'] == 'lvgfolder':
                if ts['Value'] == 'yes':
                    bucketList.append(bucket['Name'])
        for ts in tags['TagSet']:
            if ts['Key'] == 'inprogress':
                if ts['Value'] == 'yes':
                    bucketList.remove(bucket['Name'])
    return bucketList


def getConfigFile(bucket):
    res = s3client.get_object(
        Bucket=bucket,
        Key='config.json'
    )
    return json.loads(res['Body'].read())


def getFileList(bucket):
    fileList = []
    s3bucket = s3resource.Bucket(bucket)
    for s3object in s3bucket.objects.all():
        if s3object.key != 'config.json':
            fileList.append(s3object.key)
    return fileList

if __name__ == '__main__':
    foldersdb = dbresource.Table('sortingcat-folder')
    filesdb = dbresource.Table('sortingcat-items')
    bucketList = getWorkBuckets()
    for bucket in bucketList:
        promptval = raw_input('{0} : populate to DB? (y/n) > '.format(bucket))
        if promptval == 'n':
            continue
        conf = getConfigFile(bucket)
        flist = getFileList(bucket)
        random.shuffle(flist)
        for fileName in flist:
            try:
                creator = re.search('__(.+?)__', fileName).group(1)
                creator = re.sub(',', ' /', creator)
            except AttributeError:
                creator = "No Creator"
            filesdb.put_item(
                Item={
                    'folder-image': '-'.join((bucket, str(flist.index(
                        fileName)))),
                    'uptag': conf['uptag'],
                    'downtag': conf['downtag'],
                    'taptag': conf['taptag'],
                    'tagged': 'input',
                    'creator': creator,
                    'filename': fileName
                }
            )
            print "{0}: {1}".format(bucket, fileName)

        foldersdb.put_item(
            Item={
                'folder-name': bucket,
                'index': 0,
                'total': len(flist),
                'session': 0
            }
        )


