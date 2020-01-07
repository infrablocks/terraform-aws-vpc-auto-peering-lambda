import unittest

from auto_peering.vpc import VPC
from test import mocks, randoms, builders


class TestVPC(unittest.TestCase):
    def test_exposes_region_passed_at_construction(self):
        region = randoms.region()
        account_id = randoms.account_id()
        vpc_response = mocks.build_vpc_response_mock()

        vpc = VPC(vpc_response, account_id, region)

        self.assertEqual(vpc.region, region)

    def test_exposes_account_id_passed_at_construction(self):
        region = randoms.region()
        account_id = randoms.account_id()
        vpc_response = mocks.build_vpc_response_mock()

        vpc = VPC(vpc_response, account_id, region)

        self.assertEqual(vpc.account_id, account_id)

    def test_derives_component_from_vpc_tags(self):
        region = randoms.region()
        account_id = randoms.account_id()
        vpc_response = mocks.build_vpc_response_mock(
            tags=builders.build_vpc_tags(
                component="some-thing"))

        vpc = VPC(vpc_response, account_id, region)

        self.assertEqual(vpc.component, "some-thing")

    def test_derives_deployment_identifier_from_vpc_tags(self):
        region = randoms.region()
        account_id = randoms.account_id()
        vpc_response = mocks.build_vpc_response_mock(
            tags=builders.build_vpc_tags(
                deployment_identifier="platinum"))

        vpc = VPC(vpc_response, account_id, region)

        self.assertEqual(vpc.deployment_identifier, "platinum")

    def test_derives_dependencies_from_vpc_tags(self):
        region = randoms.region()
        account_id = randoms.account_id()
        dependencies = ["first-dependency", "second-dependency"]
        vpc_response = mocks.build_vpc_response_mock(
            tags=builders.build_vpc_tags(
                dependencies=dependencies))

        vpc = VPC(vpc_response, account_id, region)

        self.assertEqual(vpc.dependencies, dependencies)

    def test_generates_correctly_formatted_identifier(self):
        region = randoms.region()
        account_id = randoms.account_id()
        vpc_response = mocks.build_vpc_response_mock(
            tags=builders.build_vpc_tags(
                component='some-thing',
                deployment_identifier='platinum'
            ))

        vpc = VPC(vpc_response, account_id, region)

        self.assertEqual(
            vpc.component_instance_identifier,
            "some-thing-platinum")
