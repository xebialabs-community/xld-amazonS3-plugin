#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.elb
from os import path
def makeAWSConnection(accessId, secretKey):
  conn = S3Connection(accessId, secretKey)
  print conn
  return conn 
  
def createBucketOnS3(conn, bucketName):
  bucket = conn.create_bucket(bucketName)
  return bucket

def copyFileInS3Bucket(conn, bucketName, fileName, filePath):
  bucket = conn.get_bucket(bucketName)
  k = Key(bucket)
  k.key = fileName
  k.set_contents_from_filename(filePath)

def printContentOfS3Bucket(conn, bucketName):
  bucket = conn.get_bucket(bucketName)
  for item in bucket.list():
    print item

accessId = "${container.accessId}"
secretKey = "${container.secretKey}"
bucketName = "${container.bucketName}"
ec2Connection = makeAWSConnection(accessId, secretKey)
bucket = createBucketOnS3(ec2Connection, bucketName)
copyFileInS3Bucket(ec2Connection, bucketName, path.basename("${params.filePath}"), "${params.filePath}")
printContentOfS3Bucket(ec2Connection, bucketName)
