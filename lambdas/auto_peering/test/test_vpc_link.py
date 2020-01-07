import unittest
from unittest.mock import Mock

from auto_peering.ec2_gateway import EC2Gateway
from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from auto_peering.vpc_peering_routes import VPCPeeringRoutes
from auto_peering.vpc_link import VPCLink

from test import randoms, mocks


class TestVPCLink(unittest.TestCase):
    def test_constructs_peering_relationship_for_vpcs(self):
        vpc1 = mocks.build_vpc_response_mock(name="VPC 1")
        vpc2 = mocks.build_vpc_response_mock(name="VPC 2")

        account_id = randoms.account_id()
        region = randoms.region()

        ec2_gateways = mocks.EC2Gateways([mocks.EC2Gateway(account_id, region)])
        logger = Mock(name="Logger")

        vpc_link = VPCLink(vpc1, vpc2, ec2_gateways, logger)

        self.assertEqual(
            vpc_link.peering_relationship,
            VPCPeeringRelationship(vpc1, vpc2, ec2_gateways, logger))

    def test_constructs_peering_routes_for_peering_relationship_and_vpcs(self):
        vpc1 = mocks.build_vpc_response_mock(name="VPC 1")
        vpc2 = mocks.build_vpc_response_mock(name="VPC 2")

        account_id = randoms.account_id()
        region = randoms.region()

        ec2_gateways = mocks.EC2Gateways([mocks.EC2Gateway(account_id, region)])
        logger = Mock(name="Logger")

        vpc_link = VPCLink(vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship = vpc_link.peering_relationship

        self.assertEqual(
            vpc_link.peering_routes,
            VPCPeeringRoutes(
                vpc1, vpc2, vpc_peering_relationship,
                ec2_gateways, logger))
