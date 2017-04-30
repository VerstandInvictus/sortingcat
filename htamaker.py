import os
import re
import arrow
import boto3
import simplejson as json
import time
import config
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import random
import hydrustagarchive

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


def getFileList(bucket):
    fileList = []
    s3bucket = s3resource.Bucket(bucket)
    for s3object in s3bucket.objects.all():
        if s3object.key != 'config.json':
            fileList.append(s3object.key)
    return fileList


def getDbScanForBucket(bucket):
    filtered = list()
    res = filesdb.scan(
        FilterExpression=Key('folder-image').begins_with(bucket)
    )
    for i in res['Items']:
        filtered.append(i)
    while 'LastEvaluatedKey' in res:
        res = filesdb.scan(
            FilterExpression=Key('folder-image').begins_with(bucket),
            ExclusiveStartKey=res['LastEvaluatedKey']
        )
        for i in res['Items']:
            filtered.append(i)
    return filtered


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
    return bucketList


def processTags(hta, itemhash, tags):
    itemhash = itemhash.decode('hex')
    for tag in tags:
        hta.AddMapping(itemhash, tag)
    return

if __name__ == "__main__":
    foldersdb = dbresource.Table('sortingcat-folder')
    filesdb = dbresource.Table('sortingcat-items')
    wl = getWorkBuckets()
    for bucket in wl:
        prompt = raw_input('{0} : dump HTA? (y/n) > '.format(bucket))
        if prompt == 'y':
            htname = '{0}.db'.format(bucket)
            if os.path.exists(htname):
                os.remove(htname)
            hta = hydrustagarchive.HydrusTagArchive(htname)
            itemlist = getDbScanForBucket(bucket)
            totalitems = len(itemlist)
            print "{0} files found.".format(len(itemlist))
            count = 0
            for item in itemlist:
                print "{0} of {1}".format(count, totalitems)
                itemHash = item['filename'].split('_')[-1].split('.')[0]
                itemTags = list()
                if item['tagged'] == u'input':
                    print '''
==========
Warning: Found input tag! Bucket not complete!
{0}
==========
                          '''.format(item)
                    os.remove(htname)
                    exit()
                itemTags.append(item['tagged'])
                itemTags.append('sortbucket:{0}'.format(bucket))
                if 'extratag' in item:
                    itemTags.append(item['extratag'])
                processTags(hta, itemHash, itemTags)
                count += 1
            hta.GetNamespaces()
            prompt = raw_input('{0} : delete items from DB? (y/n) > '.format(
                bucket))
            if prompt == 'y':
                for item in itemlist:
                    filesdb.delete_item(
                        Key={
                            'folder-image': item['folder-image']
                        }
                    )
                foldersdb.delete_item(
                    Key={
                        'folder-name': bucket
                    }
                )
