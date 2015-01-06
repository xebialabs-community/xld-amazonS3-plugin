# FINRA IMPLEMENTATION SUMMARY
Oct 29, 2014 added region capabilities to S3

Jan 13 - 17, 2014

FINRA agenda consisted of the following integrations:

* Amazon ec2, s3 and elb
* LDAP
* Jenkins

...and a condensed training course


#### Customer S3 Requirements:

- Add/Delete files & folders into existing folders
- Support encrypted buckets
- Support AWS Regions

These requirements were satisfied by extending Deployit with the boto library and python scripts.

#### Customer EC2 Requirements:

Following the Deployit POC, the ec2-plugin-3.9.4 was released which included all of FINRA's required properties except:

- IAM Role Support
- Storage Support

Current status is a hotfix was made to ec2 plugin that incorporates IAM Role support and will be sent to customer for testing.


#### Customer ELB Requirements:

- Region Name
- Vm Template Name
- Instance Count
- Instance Type
- Security Group


Notes:

1. Ability to create & delete S3 buckets were developed via a synthetic.xml type and python scripts during implementation prep but customer decided to remove this feature due to internal policy restricting bucket creation (feature may be useful for other customers).  Included within the create bucket python script is a policy (using json) that requires all uploaded files to be encrypted.


```
<type type="aws.S3DeployedBucket" extends="generic.ExecutedScript" deployable-type="aws.S3Bucket" container-type="aws.S3EndPoint">
        <generate-deployable type="aws.S3Bucket" extends="generic.Resource" />
        <property name="createScript" default="aws/create_bucket.py" hidden="true" />
        <property name="destroyScript" default="aws/delete_bucket.py" hidden="true" />
        </type>

```
create_bucket.py:

```

#!/usr/bin/python

from boto.s3 import connect_to_region
from boto.s3.connection import S3Connection
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

  bucket = conn.create_bucket(bucketName, location=region)  jsonvar = json.dumps({
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
```
delete_bucket.py:

```
#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.elb
import os
from os import path
from subprocess import call
import json


def makeAWSConnection(accessId, secretKey, region):
  conn = boto.s3.connect_to_region(region, aws_access_key_id=accessId, aws_secret_access_key=secretKey, calling_format=boto.s3.connection.OrdinaryCallingFormat())
  print conn
  return conn 

def deleteBucketOnS3(conn, bucketName):
  bucket = conn.delete_bucket(bucketName)
    
def createBucketOnS3(conn, bucketName):
  bucket = conn.create_bucket(bucketName)
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
bucket = deleteBucketOnS3(ec2Connection, bucketName)

```


2
. Amazon S3 bucket naming convention prohibits use of upper-case letters for bucket names in all regions except US.  The boto library currently (as of Jan 20, 2014) does not make the disctinction of allowing lower-case bucket names even within the US region.  A workaround to this problem is to a) append the calling_format=boto.s3.connection.OrdinaryCallingFormat() command to the S3Connection() method and b) modify the boto library file connection.py within definition: def check_lowercase_bucketname(n) to comment out the following lines:


```
		#	if not (n + 'a').islower():
    	#   raise BotoClientError("Bucket names cannot contain upper-case " \
    	#   "characters when using either the sub-domain or virtual " \
    	#   "hosting calling format.")

```

### S3

Step 1: Create S3EndPoint

```
	<type type="aws.S3EndPoint" extends="overthere.LocalHost">
		<property name="accessId" default=""/>
		<property name="secretKey" password="true" default=""/>
		<property name="bucketName" default=""/>
		<property name="region" default="us-east-1"/>                  
	</type>
```

Step 2: Create aws.S3File or aws.S3Folder

```
    <type type="aws.S3DeployedContent" extends="generic.ExecutedScriptWithDerivedArtifact" deployable-type="aws.S3File" container-type="aws.S3EndPoint">
        <generate-deployable type="aws.S3File" extends="generic.File"/>
        <property name="bucket_folder" required="true" default=""/>
        <property name="createScript" default="aws/copy-to-s3_file.py" hidden="true" />
        <property name="destroyScript" default="aws/delete-s3_file.py" hidden="true" />
	</type>

	<type type="aws.S3DeployedContentFolder" extends="generic.ExecutedScriptWithDerivedArtifact" deployable-type="aws.S3Folder" container-type="aws.S3EndPoint">
        <generate-deployable type="aws.S3Folder" extends="generic.Folder"/>
        <property name="bucket_folder" required="true" default=""/>      
        <property name="createScript" default="aws/copy-to-s3_folder.py" hidden="true" />
        <property name="destroyScript" default="aws/delete-s3_folder.py" hidden="true" />
	</type>
```

Step 3: Deploy artifact to S3EndPoint Environment

### EC2

Step 1: Create ec2.Credentials

- AWS key
- AWS secret

Step 2: Create ec2.HostTemplate

Step 3: Instantiate ec2.HostTemplate

### ELB

Step 1: Create aws.ELBEndPoint

```
<type type="aws.ELBEndPoint" extends="overthere.LocalHost">
        <property name="accessId" default=""/>
        <property name="secretKey" password="true" default=""/>
        <property name="loadBalancerName" default=""/>
        <method name="addInstancesToELB" delegate="shellScript" script="aws/add-to-elb.py" label="Add Instances to ELB">
                <parameters>
                        <parameter name="regionName" default=""/>
                        <parameter name="vmTemplateName" default=""/>
                        <parameter name="instanceCount" default="2"/>
                        <parameter name="instanceType" default="t1.micro"/>
                        <parameter name="securityGroup" default=""/>
                </parameters>
        </method>
</type>
```


