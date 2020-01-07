import boto3
from functools import lru_cache


def role_arn_for(account_id, peering_role_name):
    return "arn:aws:iam::%s:role/%s" % (account_id, peering_role_name)


class SessionStore(object):
    def __init__(self, client, peering_role_name):
        self.client = client
        self.peering_role_name = peering_role_name

    @lru_cache(maxsize=32)
    def get_session_for(self, account_id):
        assumed_role_response = \
            self.client.assume_role(
                RoleArn=role_arn_for(account_id, self.peering_role_name),
                RoleSessionName="VPC Auto Peering Lambda")
        credentials = assumed_role_response['Credentials']

        return boto3.session.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
