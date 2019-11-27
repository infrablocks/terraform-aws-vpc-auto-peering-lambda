import unittest
from unittest.mock import Mock

from auto_peering.ec2_gateway import EC2Gateway
from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_routes import VPCPeeringRoutes
from auto_peering.vpc_link import VPCLink


class TestVPCLink(unittest.TestCase):
    def test_constructs_peering_relationship_for_vpcs(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        region = 'eu-west-1'
        ec2_resource = Mock(name="EC2 resource")
        ec2_client = Mock(name="EC2 client")
        ec2_gateways = {region: EC2Gateway(ec2_resource, ec2_client, region)}
        logger = Mock(name="Logger")

        vpc_link = VPCLink(vpc1, vpc2, ec2_gateways, logger)

        self.assertEqual(
            vpc_link.peering_relationship,
            VPCPeeringRelationship(vpc1, vpc2, ec2_gateways, logger))

    def test_constructs_peering_routes_for_peering_relationship_and_vpcs(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        region = 'eu-west-1'
        ec2_resource = Mock(name="EC2 resource")
        ec2_client = Mock(name="EC2 client")
        ec2_gateways = {region: EC2Gateway(ec2_resource, ec2_client, region)}
        logger = Mock(name="Logger")

        vpc_link = VPCLink(vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship = vpc_link.peering_relationship

        self.assertEqual(
            vpc_link.peering_routes,
            VPCPeeringRoutes(
                vpc1, vpc2, vpc_peering_relationship,
                ec2_gateways, logger))
