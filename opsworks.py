# cat ~/.aws/credentials
# [default]
# aws_access_key_id = AKI************DPQ
# aws_secret_access_key = EoY**********************************r6y

#!/usr/bin/python

import boto3
from botocore.exceptions import ClientError
import time
import os
import paramiko
import socket
import sys

### Generate keypait in AWS console and download it in current folder. Name of the key set below ###
pem = './opsworks.pem'
awskeyname = pem.rsplit('.pem',1)[0].rsplit('/',1)[1]

### Waiting for SSH ###
def isOpen(ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

### CREATE Security Group ###

ec2 = boto3.client('ec2')

response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    response = ec2.create_security_group(GroupName='opswork_sg_'+str(int(time.time())),
                                         Description='Security group for OpsWorks test task',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)

### CREATE EC2 instance ###
ec2 = boto3.resource('ec2',region_name="us-east-1")
instance = ec2.create_instances(
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8,
                'VolumeType': 'standard',
            },
        },
        {
            'DeviceName': '/dev/sda2',
            'VirtualName': 'opsworks_volume',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 1,
                'VolumeType': 'standard',
            },
        },
    ],
    ImageId='ami-0ac019f4fcb7cb7e6',
    KeyName=awskeyname,
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    SecurityGroupIds=[security_group_id]
    ,)
print instance[0].id
instanceId = instance[0].id
instance = ec2.Instance(id=instance[0].id)
instance.wait_until_running()
print("instance started")

PublicDnsName = boto3.client('ec2').describe_instances(InstanceIds=[instanceId])['Reservations'][0]['Instances'][0]['PublicDnsName']
print(PublicDnsName)


### Waiting for ssh and execute script remotely ###

timeout = 0
while timeout < 30:
    if isOpen(PublicDnsName,"22"):
        break
    else:
        timeout+=1
        time.sleep(1)


ssh = paramiko.SSHClient()
privkey = paramiko.RSAKey.from_private_key_file(pem)
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname = PublicDnsName, username = 'ubuntu', pkey = privkey)
# sftp = ssh.open_sftp()
# sftp.put('./mount.sh', '/home/ubuntu/mount.sh')
stdin, stdout, stderr = ssh.exec_command('hdd="/dev/xvdb"; sudo echo "n\np\n1\n\n\nw\n"|fdisk ${hdd}; sudo mkfs.ext4 "${hdd}"; sudo mkdir /mymount; sudo mount -t ext4 ${hdd} /mymount')
stdin.flush()
data = stdout.read().splitlines()
for line in data:
    x = line.decode()
    #print(line.decode())
    print(x)
    ssh.close()
