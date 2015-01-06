#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto.ec2.elb
from os import path

def connectToELB(regionName, accessId, secretKey):
  conn = boto.ec2.elb.connect_to_region(regionName,aws_access_key_id=accessId, aws_secret_access_key=secretKey)  
  return conn

def addInstancesToELB(conn, balancerName, instanceIdList):
  balancer = conn.get_all_load_balancers(load_balancer_names=[balancerName])
  balancer[0].register_instances(instanceIdList)
  print "New VM Instances added to LoadBalancer"

def createVMFromTemplate(templateName, count, regionName, accessId, secretKey, instance_typei, sec_groups):
  print " n instances created using template"
  conn = boto.ec2.connect_to_region(regionName,aws_access_key_id=accessId, aws_secret_access_key=secretKey)  
  reservation = conn.run_instances(templateName,instance_type=instance_type, max_count=count, security_groups=sec_groups)
  instanceList = []
  for instance in reservation.instances:
    print instance.id
    instanceList.extend([instance.id])
  return instanceList


accessId = "${container.accessId}"
secretKey = "${container.secretKey}"
loadBalancerName = "${container.loadBalancerName}"
regionName = "${params.regionName}"
vmTemplateName = "${params.vmTemplateName}"
count = ${params.instanceCount}
instance_type = "${params.instanceType}" 
security_groups = ["${params.securityGroup}"]
instanceIdList = createVMFromTemplate(vmTemplateName, count,regionName, accessId, secretKey, instance_type, security_groups)
elbConnection = connectToELB(regionName, accessId, secretKey)
addInstancesToELB(elbConnection, loadBalancerName, instanceIdList)
