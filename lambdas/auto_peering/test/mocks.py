import unittest.mock as mock

from test import responses, randoms, builders


def build_sts_client_mock():
    return mock.Mock(name="STS client")


def build_sts_assume_role_mock():
    credentials = randoms.credentials()

    assume_role_mock = mock.Mock(
        name='STS Assume Role',
        return_value=responses.sts_assume_role_response_for(
            access_key_id=credentials.access_key,
            secret_access_key=credentials.secret_key,
            session_token=credentials.token
        ))

    return credentials, assume_role_mock


def build_vpc_response_mock(**kwargs):
    vpc_response = mock.Mock(name=kwargs.get('name', 'VPC'))
    vpc_response.id = kwargs.get('id', randoms.vpc_id())
    vpc_response.tags = kwargs.get('tags', builders.build_vpc_tags())

    return vpc_response


class EC2Gateways(object):
    def __init__(self, ec2_gateways):
        self.ec2_gateways = ec2_gateways

    def all(self):
        return self.ec2_gateways

    def get(self, region):
        return next(ec2_gateway
                    for ec2_gateway
                    in self.ec2_gateways
                    if (ec2_gateway.region == region))

    def by_account_id_and_region(self, account_id, region):
        return next(ec2_gateway
                    for ec2_gateway
                    in self.ec2_gateways
                    if (ec2_gateway.account_id == account_id and
                        ec2_gateway.region == region))

    def by_account_id(self, account_id):
        return [ec2_gateway
                for ec2_gateway
                in self.ec2_gateways
                if (ec2_gateway.account_id == account_id)]


class EC2Gateway(object):
    def __init__(self, account_id, region):
        self.account_id = account_id
        self.region = region

        self.client_mock = mock.Mock(
            name="EC2 client for %s:%s" % (self.account_id, self.region))
        self.resource_mock = mock.Mock(
            name="EC2 resource for %s:%s" % (self.account_id, self.region))

    def client(self):
        return self.client_mock

    def resource(self):
        return self.resource_mock
