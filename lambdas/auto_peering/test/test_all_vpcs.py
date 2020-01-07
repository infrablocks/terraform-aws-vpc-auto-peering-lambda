import unittest
from unittest import mock

from auto_peering.all_vpcs import AllVPCs
from auto_peering.vpc import VPC

from test import randoms, mocks, builders


class TestAllVPCs(unittest.TestCase):
    def test_find_by_account_id_and_vpc_id(self):
        account_1_id = randoms.account_id()
        account_2_id = randoms.account_id()
        region_1_id = randoms.region()
        region_2_id = randoms.region()

        vpc_id = randoms.vpc_id()

        vpc_1_response = mocks.build_vpc_response_mock(name="VPC 1")
        vpc_2_response = mocks.build_vpc_response_mock(name="VPC 2")
        vpc_3_response = mocks.build_vpc_response_mock(name="VPC 3", id=vpc_id)
        vpc_4_response = mocks.build_vpc_response_mock(name="VPC 4")

        ec2_gateway_1_1 = mocks.EC2Gateway(account_1_id, region_1_id)
        ec2_gateway_1_2 = mocks.EC2Gateway(account_1_id, region_2_id)
        ec2_gateway_2_1 = mocks.EC2Gateway(account_2_id, region_1_id)
        ec2_gateway_2_2 = mocks.EC2Gateway(account_2_id, region_2_id)

        ec2_gateways = mocks.EC2Gateways([
            ec2_gateway_1_1, ec2_gateway_1_2, ec2_gateway_2_1, ec2_gateway_2_2,
        ])

        ec2_gateway_2_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 1 VPCs",
                return_value=[vpc_1_response, vpc_2_response])
        ec2_gateway_2_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 2 VPCs",
                return_value=[vpc_3_response, vpc_4_response])

        all_vpcs = AllVPCs(ec2_gateways)

        found_vpc = all_vpcs.find_by_account_id_and_vpc_id(account_2_id, vpc_id)

        self.assertEqual(found_vpc, VPC(vpc_3_response, )

    def test_find_by_identifier(self):
        account_1_id = randoms.account_id()
        account_2_id = randoms.account_id()
        region_1_id = randoms.region()
        region_2_id = randoms.region()

        vpc_identifier = "vpc-2-component-vpc-2-deployment-identifier"

        vpc_1 = mocks.build_vpc_response_mock(
            name="VPC 1",
            tags=builders.build_vpc_tags(
                component="vpc-1-component",
                deployment_identifier="vpc-1-deployment-identifier"))
        vpc_2 = mocks.build_vpc_response_mock(
            name="VPC 2",
            tags=builders.build_vpc_tags(
                component="vpc-2-component",
                deployment_identifier="vpc-2-deployment-identifier"))
        vpc_3 = mocks.build_vpc_response_mock(
            name="VPC 3",
            tags=builders.build_vpc_tags(
                component="vpc-3-component",
                deployment_identifier="vpc-3-deployment-identifier"))
        vpc_4 = mocks.build_vpc_response_mock(
            name="VPC 4",
            tags=builders.build_vpc_tags(
                component="vpc-4-component",
                deployment_identifier="vpc-4-deployment-identifier"))

        ec2_gateway_1_1 = mocks.EC2Gateway(account_1_id, region_1_id)
        ec2_gateway_1_2 = mocks.EC2Gateway(account_1_id, region_2_id)
        ec2_gateway_2_1 = mocks.EC2Gateway(account_2_id, region_1_id)
        ec2_gateway_2_2 = mocks.EC2Gateway(account_2_id, region_2_id)

        ec2_gateways = mocks.EC2Gateways([
            ec2_gateway_1_1, ec2_gateway_1_2, ec2_gateway_2_1, ec2_gateway_2_2,
        ])

        ec2_gateway_1_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 1 region 1 VPCs",
                return_value=[vpc_1])
        ec2_gateway_1_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 1 region 2 VPCs",
                return_value=[vpc_2])
        ec2_gateway_2_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 1 VPCs",
                return_value=[vpc_3, vpc_4])
        ec2_gateway_2_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 2 VPCs",
                return_value=[])

        all_vpcs = AllVPCs(ec2_gateways)

        found_vpc = all_vpcs.find_by_component_instance_identifier(
            vpc_identifier)

        self.assertEqual(found_vpc, vpc_2)

    def test_find_dependencies_of_vpc(self):
        account_1_id = randoms.account_id()
        account_2_id = randoms.account_id()
        region_1_id = randoms.region()
        region_2_id = randoms.region()

        target_vpc = VPC(mocks.build_vpc_response_mock(
            name="Target VPC",
            tags=builders.build_vpc_tags(
                dependencies=[
                    "component-1-deployment-2",
                    "component-4-default"
                ])), account_1_id, region_1_id)

        vpc_1_response = mocks.build_vpc_response_mock(
            name="VPC 1",
            tags=builders.build_vpc_tags(
                component="component-1",
                deployment_identifier="deployment-1"))
        vpc_2_response = mocks.build_vpc_response_mock(
            name="VPC 2",
            tags=builders.build_vpc_tags(
                component="component-1",
                deployment_identifier="deployment-2"))
        vpc_3_response = mocks.build_vpc_response_mock(
            name="VPC 3",
            tags=builders.build_vpc_tags(
                component="component-2",
                deployment_identifier="deployment-1"))
        vpc_4_response = mocks.build_vpc_response_mock(
            name="VPC 4",
            tags=builders.build_vpc_tags(
                component="component-4",
                deployment_identifier="default"))

        ec2_gateway_1_1 = mocks.EC2Gateway(account_1_id, region_1_id)
        ec2_gateway_1_2 = mocks.EC2Gateway(account_1_id, region_2_id)
        ec2_gateway_2_1 = mocks.EC2Gateway(account_2_id, region_1_id)
        ec2_gateway_2_2 = mocks.EC2Gateway(account_2_id, region_2_id)

        ec2_gateways = mocks.EC2Gateways([
            ec2_gateway_1_1, ec2_gateway_1_2, ec2_gateway_2_1, ec2_gateway_2_2,
        ])

        ec2_gateway_1_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 1 region 1 VPCs",
                return_value=[vpc_1_response])
        ec2_gateway_1_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 1 region 2 VPCs",
                return_value=[vpc_2_response])
        ec2_gateway_2_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 1 VPCs",
                return_value=[vpc_3_response, vpc_4_response])
        ec2_gateway_2_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 2 VPCs",
                return_value=[])

        all_vpcs = AllVPCs(ec2_gateways)

        found_vpcs = all_vpcs.find_dependencies_of(target_vpc)

        self.assertEqual(
            set(found_vpcs),
            {vpc_2_response, vpc_4_response})

    def test_find_dependents_of_vpc(self):
        account_1_id = randoms.account_id()
        account_2_id = randoms.account_id()
        region_1_id = randoms.region()
        region_2_id = randoms.region()

        target_vpc = with_metadata(mocks.build_vpc_response_mock(
            name="Target VPC",
            tags=builders.build_vpc_tags(
                component="target",
                deployment_identifier="default"
            )), account_1_id, region_1_id)

        vpc_1 = mocks.build_vpc_response_mock(
            name="VPC 1",
            tags=builders.build_vpc_tags(
                dependencies=["target-default", "other-thing"]))
        vpc_2 = mocks.build_vpc_response_mock(
            name="VPC 2",
            tags=builders.build_vpc_tags(
                dependencies=[]))
        vpc_3 = mocks.build_vpc_response_mock(
            name="VPC 3",
            tags=builders.build_vpc_tags(
                dependencies=[]))
        vpc_4 = mocks.build_vpc_response_mock(
            name="VPC 4",
            tags=builders.build_vpc_tags(
                dependencies=["other-thing", "target-default"]))

        ec2_gateway_1_1 = mocks.EC2Gateway(account_1_id, region_1_id)
        ec2_gateway_1_2 = mocks.EC2Gateway(account_1_id, region_2_id)
        ec2_gateway_2_1 = mocks.EC2Gateway(account_2_id, region_1_id)
        ec2_gateway_2_2 = mocks.EC2Gateway(account_2_id, region_2_id)

        ec2_gateways = mocks.EC2Gateways([
            ec2_gateway_1_1, ec2_gateway_1_2, ec2_gateway_2_1, ec2_gateway_2_2,
        ])

        ec2_gateway_1_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 1 region 1 VPCs",
                return_value=[vpc_1])
        ec2_gateway_1_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 1 region 2 VPCs",
                return_value=[vpc_2])
        ec2_gateway_2_1.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 1 VPCs",
                return_value=[vpc_3, vpc_4])
        ec2_gateway_2_2.resource().vpcs.all = \
            mock.Mock(
                name="Account 2 region 2 VPCs",
                return_value=[])

        all_vpcs = AllVPCs(ec2_gateways)

        found_vpcs = all_vpcs.find_dependents_of(target_vpc)

        self.assertEqual(
            set(found_vpcs),
            {vpc_1, vpc_4})
