from botocore.exceptions import ClientError


class VPCPeeringRelationship(object):
    def __init__(self, vpc1, vpc2, ec2_gateways, logger):
        self.vpc1 = vpc1
        self.vpc2 = vpc2
        self.ec2_gateways = ec2_gateways
        self.logger = logger

    def __peering_connection_for(self, vpc1, vpc2):
        ec2_gateway = self.ec2_gateways.get(vpc1.region)
        ec2_resource = ec2_gateway.resource

        return next(
            iter(ec2_resource.vpc_peering_connections.filter(
                Filters=[{'Name': 'accepter-vpc-info.vpc-id',
                          'Values': [vpc1.id]},
                         {'Name': 'requester-vpc-info.vpc-id',
                          'Values': [vpc2.id]}])),
            None)

    def fetch(self):
        peering_connection = self.__peering_connection_for(
            self.vpc1, self.vpc2)
        if peering_connection:
            return peering_connection

        peering_connection = self.__peering_connection_for(
            self.vpc2, self.vpc1)
        if peering_connection:
            return peering_connection

        return None

    def provision(self):
        vpc1_id = self.vpc1.id
        vpc2_id = self.vpc2.id

        vpc2_region = self.vpc2.region

        self.logger.debug(
            "Requesting peering connection between: '%s' and: '%s'.",
            vpc1_id, vpc2_id)
        requester_vpc_peering_connection = self. \
            vpc1.request_vpc_peering_connection(PeerVpcId=vpc2_id,
                                                PeerRegion=vpc2_region)

        try:
            ec2_gateway = self.ec2_gateways.get(vpc2_region)
            ec2_resource = ec2_gateway.resource
            ec2_client = ec2_gateway.client

            vpc_peering_connection_id = requester_vpc_peering_connection.id

            self.logger.debug(
                "Waiting for peering connection between: '%s' and: '%s' to "
                "exist.",
                vpc1_id, vpc2_id)
            waiter = ec2_client.get_waiter('vpc_peering_connection_exists')
            waiter.wait(
                VpcPeeringConnectionIds=[vpc_peering_connection_id],
                WaiterConfig={'Delay': 2, 'MaxAttempts': 10})

            self.logger.debug(
                "Accepting peering connection between: '%s' and: '%s'.",
                vpc1_id, vpc2_id)

            acceptor_vpc_peering_connection = next(iter(
                ec2_resource.vpc_peering_connections.filter(
                    VpcPeeringConnectionIds=[
                        vpc_peering_connection_id
                    ])), None)
            acceptor_vpc_peering_connection.accept()
        except ClientError as error:
            self.logger.warn(
                "Could not accept peering connection. Error was: %s.",
                vpc1_id, vpc2_id, error)
            requester_vpc_peering_connection.delete()

    def destroy(self):
        vpc_peering_connection = self.fetch()
        if vpc_peering_connection:
            self.logger.debug(
                "Destroying peering connection between: '%s' and: '%s'",
                vpc_peering_connection.requester_vpc.id,
                vpc_peering_connection.accepter_vpc.id)
            vpc_peering_connection.delete()
        else:
            self.logger.debug(
                "No peering connection to destroy between: '%s' and: '%s'",
                self.vpc1.id,
                self.vpc2.id)

    def perform(self, action):
        getattr(self, action)()

    def _to_dict(self):
        return {
            'vpcs': frozenset([self.vpc1, self.vpc2])
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._to_dict() == other._to_dict()
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self._to_dict().items())))
