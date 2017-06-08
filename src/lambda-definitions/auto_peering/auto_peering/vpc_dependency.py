from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_routes import VPCPeeringRoutes


class VPCDependency(object):
    def __init__(self, vpc1, vpc2, ec2_client, logger):
        self.peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        self.peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, self.peering_relationship,
            ec2_client, logger)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
