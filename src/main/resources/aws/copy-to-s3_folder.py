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
  
def copyFileInS3Bucket(conn, bucketName, fileName, filePath):
  bucket = conn.get_bucket(bucketName)
  k = Key(bucket)
  k.key = folder + '/' + fileName
  k.encrypt_key = True
  k.set_contents_from_filename(filePath, encrypt_key=True)

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
      copyFileInS3Bucket(ec2Connection, bucketName, relpath, fullpath)
      

accessId = "${deployed.container.accessId}"
secretKey = "${deployed.container.secretKey}"
bucketName = "${deployed.container.bucketName}"
folder = "${deployed.bucket_folder}"
region = "${deployed.container.region}"
ec2Connection = makeAWSConnection(accessId, secretKey, region)
filename = path.basename("${deployed.file}")
basedir = "${deployed.file}"
scandir(basedir)

#for filedir in os.listdir(filename):
#   if os.path.isdir("${deployed.file}/" + filedir):
#      print "found directory: " + filedir
#      print "call recursive search and copy definition"
#      
#   if os.path.isfile("${deployed.file}/" + filedir):
#      print "found file: " + filedir
#   print "file= " + filedir
#   print "filename= " + filename
#   print "deployed.file= " + "${deployed.file}"

