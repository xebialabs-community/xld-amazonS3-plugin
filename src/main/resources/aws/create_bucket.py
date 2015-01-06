#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3 import connect_to_region
from boto.s3.key import Key
import boto.ec2.elb
import os
from os import path
from subprocess import call
import json


def makeAWSConnection(accessId, secretKey, region):
  conn = connect_to_region(region, aws_access_key_id=accessId, aws_secret_access_key=secretKey, calling_format=boto.s3.connection.OrdinaryCallingFormat())
  print conn
  return conn 


def deleteBucketOnS3(conn, bucketName):
  bucket = conn.create_bucket(bucketName)
  delete_bucket(bucketName)
    
def createBucketOnS3(conn, bucketName, region):

  bucket = conn.create_bucket(bucketName, location=region)
  jsonvar = json.dumps({
   "Version":"2012-10-17",
   "Id":"PutObjPolicy",
   "Statement":[{
         "Sid":"DenyUnEncryptedObjectUploads",
         "Effect":"Deny",
         "Principal":{
            "AWS":"*"
         },
         "Action":"s3:PutObject",
         "Resource":"arn:aws:s3:::%s/*",
         "Condition":{
            "StringNotEquals":{
               "s3:x-amz-server-side-encryption":"AES256"
            }
         }
      }
   ]
  })
  
  # now set bucket policy to require encrypted objects
  bucket.set_policy(jsonvar % bucketName)
  print bucket.get_policy()
  return bucket

def copyFileInS3Bucket(conn, bucketName, fileName, filePath):
  bucket = conn.get_bucket(bucketName)
  k = Key(bucket)
  k.key = fileName
  k.encrypt_key = True
  k.set_contents_from_filename(filePath, encrypt_key=True)

def printContentOfS3Bucket(conn, bucketName):
  bucket = conn.get_bucket(bucketName)
  for item in bucket.list():
    print item
    

accessId = "${deployed.container.accessId}"
secretKey = "${deployed.container.secretKey}"
bucketName = "${deployed.container.bucketName}"
region = "${deployed.container.region}"
ec2Connection = makeAWSConnection(accessId, secretKey, region)
bucket = createBucketOnS3(ec2Connection, bucketName, region)
#bucket = createBucketOnS3(ec2Connection, bucketName)

