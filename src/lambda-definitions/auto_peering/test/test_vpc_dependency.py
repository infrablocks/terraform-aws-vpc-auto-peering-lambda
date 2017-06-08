import unittest
from unittest.mock import Mock

from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_routes import VPCPeeringRoutes
from auto_peering.vpc_dependency import VPCDependency


class TestVPCDependency(unittest.TestCase):
    def test_constructs_peering_relationship_for_vpcs(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        ec2_client = Mock(name="EC2 client")
        logger = Mock(name="Logger")

        vpc_dependency = VPCDependency(vpc1, vpc2, ec2_client, logger)

        self.assertEqual(
            vpc_dependency.peering_relationship,
            VPCPeeringRelationship(vpc1, vpc2, ec2_client, logger))

    def test_constructs_peering_routes_for_peering_relationship_and_vpcs(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        ec2_client = Mock(name="EC2 client")
        logger = Mock(name="Logger")

        vpc_dependency = VPCDependency(vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship = vpc_dependency.peering_relationship

        self.assertEqual(
            vpc_dependency.peering_routes,
            VPCPeeringRoutes(
                vpc1, vpc2, vpc_peering_relationship,
                ec2_client, logger))
