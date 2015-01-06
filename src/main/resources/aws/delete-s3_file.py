#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.elb
from os import path

def makeAWSConnection(accessId, secretKey, region):
  conn = boto.s3.connect_to_region(region, aws_access_key_id=accessId, aws_secret_access_key=secretKey, calling_format=boto.s3.connection.OrdinaryCallingFormat())
  print conn
  return conn 

def delFileInS3Bucket(conn, bucketName, fileName, filePath):
  bucket = conn.get_bucket(bucketName)
  k = Key(bucket)
  k.key = folder + '/' + fileName
  print k.key
  bucket.delete_key(k.key)
      
def printContentOfS3Bucket(conn, bucketName):
  bucket = conn.get_bucket(bucketName)
  for item in bucket.list():
    print item

accessId = "${deployed.container.accessId}"
secretKey = "${deployed.container.secretKey}"
bucketName = "${deployed.container.bucketName}"
folder = "${deployed.bucket_folder}"
region = "${deployed.container.region}"
ec2Connection = makeAWSConnection(accessId, secretKey, region)
delFileInS3Bucket(ec2Connection, bucketName, path.basename("${deployed.file}"), "${deployed.file}")
printContentOfS3Bucket(ec2Connection, bucketName)
