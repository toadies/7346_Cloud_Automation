import uuid
import subprocess    
import os
from dotenv import load_dotenv
import paramiko
load_dotenv(dotenv_path="../.env")

def aws_create_bucket_name(bucket_name):
    """Creta a unique bucket name
    Keyword arguments:
    bucket_name: string
    return name + uuid string
    """
    return '-'.join([bucket_name, str(uuid.uuid4())])

def aws_create_bucket(bucket_name, s3_connection, current_region):
    """Create an AWS Bucket
    Keyword arguments:
    bucket name: string
    s3_connection: boto3 S3 Resource
    return bucket_name, bucket_response
    """
    # Create Configurations
    configs = {}
    if current_region != "us-east-1":
        config["LocationConstraint"] = current_region

    bucket_name = aws_create_bucket_name(bucket_name)
    
    if current_region == "us-east-1":
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name)
    else:
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint":current_region})
        
    print(bucket_name, current_region)
    return bucket_name, bucket_response

def aws_upload_files_to_bucket(path_to_src, bucket_name):
    """Use AWS CLI to sync a local folder to AWS Bucket"""
    path_to_s3 = "s3://" + bucket_name

    try:
        result = os.popen('aws s3 sync '+path_to_src+' '+path_to_s3+' --exclude "model/*" --acl private').read()
        print(result)
        return True
    except:
        print("upload failed")
        return False

def aws_list_objects(bucket_name, s3_resource):
    bucket=s3_resource.Bucket(bucket_name)
    res = []
    for obj_version in bucket.object_versions.all():
        res.append({
            'file_name': obj_version.object_key,
            'VersionId': obj_version.id
        })
    return res, bucket

def aws_delete_all_objects(bucket_name, s3_resource):
    """Delete all objects inside a bucket"""
    resources, bucket = aws_list_objects(bucket_name, s3_resource)
    bucket.delete_objects(Delete={'Objects': resources})
    return bucket

def aws_delete_bucket(bucket_name, s3_resource):
    """delete bucket and all its content"""
    bucket = aws_delete_all_objects(bucket_name, s3_resource)
    bucket.delete()

def aws_list_buckets(bucket_name, s3_resource):
    return s3_resource.buckets.all()

def aws_download_objects(path_to_src, bucket_name):
    """Use AWS CLI to sync a local folder to AWS Bucket"""
    path_to_s3 = "s3://" + bucket_name

    try:
        result = os.popen('aws s3 sync '+path_to_s3+' '+path_to_src).read()
        print(result)
        return True
    except:
        print("upload failed")
        return False  

def aws_create_ec2_name(bucket_prefix):
    """Create a unique ec2 name"""
    return '-'.join([bucket_prefix, str(uuid.uuid4())])

def aws_user_data_script(bucket_name):
    user_data = [
        "#cloud-boothook",
        "#!/bin/bash",
        "yum update -q -y",
        "yum install automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel -q -y",
        "git clone https://github.com/s3fs-fuse/s3fs-fuse.git /tmp/s3fs-fuse",
        "cd /tmp/s3fs-fuse",
        "./autogen.sh",
        "./configure --prefix=/usr --with-openssl",
        "make",
        "make install",
        'echo "' + os.getenv("AWS_ACCESS_ID") + ':' + os.getenv("AWS_SECRET_ACCESS_KEY") + '" > /tmp/passwd-s3fs',
        "mv -f /tmp/passwd-s3fs /etc",
        "chmod 640 /etc/passwd-s3fs",
        "mkdir -p /mys3bucket",
        "chown ec2-user:ec2-user /mys3bucket",
        "s3fs " + bucket_name + " -o use_cache=/tmp -o uid=500 -o mp_umask=002 -o multireq_max=5 -o allow_other /mys3bucket",
        # "while read requirement; do conda install --yes $requirement; done < /mys3bucket/requirements.txt"
    ]
    return "\n".join(user_data)

def aws_create_ec2_instance(ec2_name, security_group, user_data, ec2_resource, image_id = "ami-062c42cbecc1d5ec0", instance_type="t2.medium"):
    pem_key =  os.getenv("AWS_PEM_KEY")
    ec2_name = aws_create_ec2_name(ec2_name)

    instances = ec2_resource.create_instances(
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': ec2_name
                    },
                ]
            }
        ],
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
    #     InstanceType='t2.medium',
        KeyName=pem_key,
        SecurityGroupIds=security_group, #Bring your own!
        UserData=user_data
    )

    return instances[0]

def aws_stop_ec2(instance_id, ec2_client):
    return ec2_client.stop_instances(
        InstanceIds=[
            instance_id,
        ]
    )

def exec_ssh_cmd(public_dns_name = "", commands = ""):
    pem_key = os.getenv("AWS_PEM_KEY")
    pem_location = os.getenv("AWS_PEM_LOCATION")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file(pem_location+pem_key+'.pem')
    ssh.connect(public_dns_name,username="ec2-user",pkey=privkey)
    
    result = []
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.flush()
        data = stdout.read().splitlines()
        data = [l.decode("utf-8") for l in data]

        result.append({"cmd":cmd,"response":data})

    ssh.close()
    return result