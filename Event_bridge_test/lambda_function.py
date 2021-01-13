import boto3

region = 'ap-northeast-1'
# 下記、EventBridgeから受け取ったEC2のIDを受け取るようにする。(追記必要)
instances = ['TARGET_EC2_ID']
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    ec2.start_instances(InstanceIds=instances)
    print('started your instances: ' + str(instances))