#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.elb
import os
from os import path
from subprocess import call

def makeAWSConnection(accessId, secretKey, region):
  conn = boto.s3.connect_to_region(region, aws_access_key_id=accessId, aws_secret_access_key=secretKey, calling_format=boto.s3.connection.OrdinaryCallingFormat())
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
    
def scandir(currdir):
  #print "current dir: " + currdir
  for thisfiledir in os.listdir(currdir):
    #print "inside listdir, thisfiledir: " + thisfiledir
    if os.path.isdir(currdir + "/" + thisfiledir):
      #print "found dir: " + currdir + "/" + thisfiledir
      scandir(currdir + "/" + thisfiledir)
    if os.path.isfile(currdir + "/" + thisfiledir):
      fullpath = currdir + "/" + thisfiledir
      print "fullpath: " + fullpath
      relpath = os.path.relpath(fullpath,"${deployed.file}")
      #relpath = text.split(fullpath, "${deployed.file}")[0]
      print "rel path: " + relpath
      #print "found file: " + currdir + "/" + thisfiledir
      print "basename: " + path.basename("${deployed.file}")
      delFileInS3Bucket(ec2Connection, bucketName, relpath, fullpath)

def delFileInS3Bucket(conn, bucketName, fileName, filePath):
  bucket = conn.get_bucket(bucketName)
  k = Key(bucket)
  k.key = folder + '/' + fileName
  bucket.delete_key(k.key)      

accessId = "${deployed.container.accessId}"
secretKey = "${deployed.container.secretKey}"
bucketName = "${deployed.container.bucketName}"
folder = "${deployed.bucket_folder}"
region = "${deployed.container.region}"
ec2Connection = makeAWSConnection(accessId, secretKey, region)
filename = path.basename("${deployed.file}")
basedir = "${deployed.file}"
scandir(basedir)
