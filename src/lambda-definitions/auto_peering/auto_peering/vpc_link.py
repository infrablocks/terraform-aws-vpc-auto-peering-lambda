from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_routes import VPCPeeringRoutes


class VPCLink(object):
    def __init__(self, vpc1, vpc2, ec2, logger):
        self.vpc1 = vpc1
        self.vpc2 = vpc2
        self.peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2, logger)
        self.peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, self.peering_relationship,
            ec2, logger)

    def _to_dict(self):
        return {
            'vpcs': frozenset([self.vpc1, self.vpc2]),
            'peering_relationship': self.peering_relationship,
            'peering_routes': self.peering_routes
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
