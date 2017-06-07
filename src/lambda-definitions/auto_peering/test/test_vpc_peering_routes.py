import unittest
from unittest.mock import Mock
from botocore.exceptions import ClientError

from auto_peering.vpc_peering_routes import VPCPeeringRoutes


def mock_filter_for(**kwargs):
    vpc1 = kwargs['vpc1']
    vpc2 = kwargs['vpc2']

    vpc1_route_tables = kwargs['vpc1_route_tables']
    vpc2_route_tables = kwargs['vpc2_route_tables']

    def conditionally_return_route_tables(**filters):
        vpc1_filters = {
            'Filters': [
                {'Name': 'vpc-id', 'Values': [vpc1.id]},
                {'Name': 'tag:Tier', 'Values': ['private']}]}

        vpc2_filters = {
            'Filters': [
                {'Name': 'vpc-id', 'Values': [vpc2.id]},
                {'Name': 'tag:Tier', 'Values': ['private']}]}

        if filters == vpc1_filters:
            return iter(vpc1_route_tables)

        if filters == vpc2_filters:
            return iter(vpc2_route_tables)

        raise Exception(
            "No matching route tables for filters: {}".format(filters))

    return conditionally_return_route_tables


def mock_route_for(*definitions):
    def route_constructor(route_table_id, destination_cidr):
        for definition in definitions:
            if definition['arguments'] == [route_table_id, destination_cidr]:
                return definition['return']

        raise Exception(
            "No matching route for arguments: {}, {}".format(
                route_table_id, destination_cidr))

    return route_constructor


class TestVPCPeeringRoutesProvision(unittest.TestCase):
    def test_creates_routes_in_vpc1_for_vpc2_via_peering_connection(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")

        ec2_client = Mock()
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_2 = Mock(name="VPC 1 route table 2")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")
        vpc2_route_table_2 = Mock(name="VPC 2 route table 2")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1,
                vpc1_route_tables=[vpc1_route_table_1, vpc1_route_table_2],
                vpc2=vpc2,
                vpc2_route_tables=[vpc2_route_table_1, vpc2_route_table_2]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.provision()
        vpc1_route_table_1.create_route.assert_called_with(
            DestinationCidrBlock=vpc2.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

        vpc1_route_table_2.create_route.assert_called_with(
            DestinationCidrBlock=vpc2.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

    def test_creates_routes_in_vpc2_for_vpc1_via_peering_connection(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        ec2_client = Mock()
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_2 = Mock(name="VPC 1 route table 2")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")
        vpc2_route_table_2 = Mock(name="VPC 2 route table 2")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1,
                vpc1_route_tables=[vpc1_route_table_1, vpc1_route_table_2],
                vpc2=vpc2,
                vpc2_route_tables=[vpc2_route_table_1, vpc2_route_table_2]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.provision()
        vpc2_route_table_1.create_route.assert_called_with(
            DestinationCidrBlock=vpc1.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

        vpc2_route_table_2.create_route.assert_called_with(
            DestinationCidrBlock=vpc1.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

    def test_handles_no_matching_route_tables(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")
        ec2_client = Mock()
        logger = Mock()

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1, vpc1_route_tables=[],
                vpc2=vpc2, vpc2_route_tables=[]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        try:
            vpc_peering_routes.provision()
        except Exception as exception:
            self.fail(
                'Expected no exception but encountered: {0}'.format(exception))

    def test_logs_that_routes_are_being_added_for_a_vpc(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")

        ec2_client = Mock()
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1, vpc1_route_tables=[vpc1_route_table_1],
                vpc2=vpc2, vpc2_route_tables=[]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.provision()

        logger.debug.assert_any_call(
            "Adding routes to private subnets in: '%s' pointing at '%s:%s:%s'.",
            vpc1.id, vpc2.id, vpc2.cidr_block, vpc_peering_connection.id)

    def test_logs_that_route_creation_succeeded(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")

        ec2_client = Mock()
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1, vpc1_route_tables=[vpc1_route_table_1],
                vpc2=vpc2, vpc2_route_tables=[]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.provision()

        logger.debug.assert_any_call(
            "Route creation succeeded for '%s'. Continuing.",
            vpc1_route_table_1.id)

    def test_logs_that_route_creation_failed_and_continues_on_exception(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")

        ec2_client = Mock()
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1,
                vpc1_route_tables=[vpc1_route_table_1],
                vpc2=vpc2,
                vpc2_route_tables=[vpc2_route_table_1]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc1_route_table_1.create_route = Mock(
            side_effect=ClientError({'Error': {'Code': '123'}}, 'something'))

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.provision()

        logger.warn.assert_any_call(
            "Route creation failed for '%s'. It may already exist. Continuing.",
            vpc1_route_table_1.id)

        vpc2_route_table_1.create_route.assert_called_with(
            DestinationCidrBlock=vpc1.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)


class TestVPCPeeringRoutesDestroy(unittest.TestCase):
    def test_destroys_routes_in_vpc1_for_vpc2_via_peering_connection(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")

        ec2_client = Mock()
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_2 = Mock(name="VPC 1 route table 2")

        vpc1_route_table_1_route = Mock(name="VPC 1 route table 1 route")
        vpc1_route_table_2_route = Mock(name="VPC 1 route table 2 route")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1,
                vpc1_route_tables=[vpc1_route_table_1, vpc1_route_table_2],
                vpc2=vpc2, vpc2_route_tables=[]))

        ec2_client.Route = Mock(
            name="Route constructor",
            side_effect=mock_route_for(
                {'arguments': [vpc1_route_table_1.id, vpc2.cidr_block],
                 'return': vpc1_route_table_1_route},
                {'arguments': [vpc1_route_table_2.id, vpc2.cidr_block],
                 'return': vpc1_route_table_2_route}))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.destroy()

        vpc1_route_table_1_route.delete.assert_called()
        vpc1_route_table_2_route.delete.assert_called()

    def test_destroys_routes_in_vpc2_for_vpc1_via_peering_connection(self):
        vpc1 = Mock(name="VPC 1")
        vpc2 = Mock(name="VPC 2")

        ec2_client = Mock()
        logger = Mock()

        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")
        vpc2_route_table_2 = Mock(name="VPC 2 route table 2")

        vpc2_route_table_1_route = Mock(name="VPC 2 route table 1 route")
        vpc2_route_table_2_route = Mock(name="VPC 2 route table 2 route")

        ec2_client.route_tables = Mock(name="VPC route tables")
        ec2_client.route_tables.filter = Mock(
            name="Filtered VPC route tables",
            side_effect=mock_filter_for(
                vpc1=vpc1, vpc1_route_tables=[],
                vpc2=vpc2,
                vpc2_route_tables=[vpc2_route_table_1, vpc2_route_table_2]))

        ec2_client.Route = Mock(
            name="Route constructor",
            side_effect=mock_route_for(
                {'arguments': [vpc2_route_table_1.id, vpc1.cidr_block],
                 'return': vpc2_route_table_1_route},
                {'arguments': [vpc2_route_table_2.id, vpc1.cidr_block],
                 'return': vpc2_route_table_2_route}))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_client, logger)

        vpc_peering_routes.destroy()

        vpc2_route_table_1_route.delete.assert_called()
        vpc2_route_table_2_route.delete.assert_called()
