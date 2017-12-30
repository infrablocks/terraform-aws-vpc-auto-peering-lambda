import unittest
from unittest.mock import Mock

from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_routes import VPCPeeringRoutes
from auto_peering.vpc_link import VPCLink


class TestVPCLink(unittest.TestCase):
    def test_constructs_peering_relationship_for_vpcs(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        ec2 = Mock(name="EC2 client")
        logger = Mock(name="Logger")

        vpc_link = VPCLink(vpc1, vpc2, ec2, logger)

        self.assertEqual(
            vpc_link.peering_relationship,
            VPCPeeringRelationship(vpc1, vpc2, ec2, logger))

    def test_constructs_peering_routes_for_peering_relationship_and_vpcs(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        ec2 = Mock(name="EC2 client")
        logger = Mock(name="Logger")

        vpc_link = VPCLink(vpc1, vpc2, ec2, logger)
        vpc_peering_relationship = vpc_link.peering_relationship

        self.assertEqual(
            vpc_link.peering_routes,
            VPCPeeringRoutes(
                vpc1, vpc2, vpc_peering_relationship,
                ec2, logger))
