import boto3
from exceptions import EC2Error


class EC2Module:
    def __init__(self, region, instance_id):
        self.region = region
        self.instance_id = instance_id
        self.ec2 = boto3.client("ec2", region_name=self.region)

    def start_instance(self):
        try:
            response = self.ec2.start_instances(InstanceIds=[self.instance_id])
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                for instance in response['StartingInstances']:
                    current_state = instance['CurrentState']['Name']
                    prev_state = instance['PreviousState']['Name']
                    instance_id = instance['InstanceId']
                return f"Instance {instance_id} has changed from {prev_state} to {current_state}."
            else:
                return "Failed to start the instance."
        except Exception as e:
            raise EC2Error(str(e))

    def stop_instance(self):
        try:
            response = self.ec2.stop_instances(InstanceIds=[self.instance_id])
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                for instance in response['StoppingInstances']:
                    current_state = instance['CurrentState']['Name']
                    prev_state = instance['PreviousState']['Name']
                    instance_id = instance['InstanceId']
                return f"Instance {instance_id} has changed from {prev_state} to {current_state}."
            else:
                return "Failed to stop the instance."
        except Exception as e:
            raise EC2Error(str(e))
