from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_route import VPCPeeringRoute


class VPCLink(object):
    def __init__(self, ec2_gateways, logger, between, routes):
        self.between = between
        self.peering_relationship = VPCPeeringRelationship(
            ec2_gateways,
            logger,
            between=between)
        self.peering_routes = [
            VPCPeeringRoute(
                ec2_gateways,
                logger,
                between=route,
                peering_relationship=self.peering_relationship)
            for route in routes
        ]

    def _to_dict(self):
        return {
            'vpcs': tuple(self.between),
            'peering_relationship': self.peering_relationship,
            'peering_routes': tuple(self.peering_routes)
        }

    def __repr__(self):
        return str(self._to_dict())

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
