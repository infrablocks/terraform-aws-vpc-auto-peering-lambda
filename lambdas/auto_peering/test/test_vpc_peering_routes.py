import unittest
from unittest.mock import Mock
from botocore.exceptions import ClientError

from auto_peering.vpc import VPC
from auto_peering.vpc_peering_routes import VPCPeeringRoutes
from test import randoms, mocks

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
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_2 = Mock(name="VPC 1 route table 2")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")
        vpc2_route_table_2 = Mock(name="VPC 2 route table 2")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc1_route_table_1, vpc1_route_table_2]))

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc2_route_table_1, vpc2_route_table_2]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.provision()
        vpc1_route_table_1.create_route.assert_called_with(
            DestinationCidrBlock=vpc2.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

        vpc1_route_table_2.create_route.assert_called_with(
            DestinationCidrBlock=vpc2.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

    def test_creates_routes_in_vpc2_for_vpc1_via_peering_connection(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_2 = Mock(name="VPC 1 route table 2")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")
        vpc2_route_table_2 = Mock(name="VPC 2 route table 2")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc1_route_table_1, vpc1_route_table_2]))

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=([vpc2_route_table_1, vpc2_route_table_2]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.provision()
        vpc2_route_table_1.create_route.assert_called_with(
            DestinationCidrBlock=vpc1.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

        vpc2_route_table_2.create_route.assert_called_with(
            DestinationCidrBlock=vpc1.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)

    def test_handles_no_matching_route_tables(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([]))

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        try:
            vpc_peering_routes.provision()
        except Exception as exception:
            self.fail(
                'Expected no exception but encountered: {0}'.format(exception))

    def test_logs_that_routes_are_being_added_for_a_vpc(self):
        region_1 = randoms.region()
        region_2 = randoms.region()
        account_id = randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc1_route_table_1]))

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.provision()

        logger.debug.assert_any_call(
            "Adding routes to private subnets in: '%s' pointing at '%s:%s:%s'.",
            vpc1.id, vpc2.id, vpc2.cidr_block, vpc_peering_connection.id)

    def test_logs_that_route_creation_succeeded(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc1_route_table_1]))

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.provision()

        logger.debug.assert_any_call(
            "Route creation succeeded for '%s'. Continuing.",
            vpc1_route_table_1.id)

    def test_logs_that_route_creation_failed_and_continues_on_exception(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc1_route_table_1]))

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=iter([vpc2_route_table_1]))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        create_route_error = \
            ClientError({'Error': {'Code': '123'}}, 'something')
        vpc1_route_table_1.create_route = Mock(
            side_effect=create_route_error)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.provision()

        logger.warn.assert_any_call(
            "Route creation failed for '%s'. Error was: %s",
            vpc1_route_table_1.id, create_route_error)

        vpc2_route_table_1.create_route.assert_called_with(
            DestinationCidrBlock=vpc1.cidr_block,
            VpcPeeringConnectionId=vpc_peering_connection.id)


class TestVPCPeeringRoutesDestroy(unittest.TestCase):
    def test_destroys_routes_in_vpc1_for_vpc2_via_peering_connection(self):
        region_1 = randoms.region()
        region_2 = randoms.region()
        account_id = randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_2 = Mock(name="VPC 1 route table 2")

        vpc1_route_table_1.id = randoms.route_table_id()
        vpc1_route_table_2.id = randoms.route_table_id()

        vpc1_route_table_1_route = Mock(name="VPC 1 route table 1 route")
        vpc1_route_table_2_route = Mock(name="VPC 1 route table 2 route")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[vpc1_route_table_1, vpc1_route_table_2])

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[])

        ec2_gateway_1.resource().Route = Mock(
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
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.destroy()

        vpc1_route_table_1_route.delete.assert_called()
        vpc1_route_table_2_route.delete.assert_called()

    def test_destroys_routes_in_vpc2_for_vpc1_via_peering_connection(self):
        region_1 = randoms.region()
        region_2 = randoms.region()
        account_id = randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")
        vpc2_route_table_2 = Mock(name="VPC 2 route table 2")

        vpc2_route_table_1_route = Mock(name="VPC 2 route table 1 route")
        vpc2_route_table_2_route = Mock(name="VPC 2 route table 2 route")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[])

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[vpc2_route_table_1, vpc2_route_table_2])

        ec2_gateway_2.resource().Route = Mock(
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
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.destroy()

        vpc2_route_table_1_route.delete.assert_called()
        vpc2_route_table_2_route.delete.assert_called()

    def test_handles_no_matching_route_tables(self):
        region_1 = randoms.region()
        region_2 = randoms.region()
        account_id = randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[])

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[])

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        try:
            vpc_peering_routes.destroy()
        except Exception as exception:
            self.fail(
                'Expected no exception but encountered: {0}'.format(exception))

    def test_logs_that_routes_are_being_deleted_for_a_vpc(self):
        region_1 = randoms.region()
        region_2 = randoms.region()
        account_id = randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_1_route = Mock(name="VPC 1 route table 1 route")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[vpc1_route_table_1])

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[])

        ec2_gateway_1.resource().Route = Mock(
            name="Route constructor",
            side_effect=mock_route_for(
                {'arguments': [vpc1_route_table_1.id, vpc2.cidr_block],
                 'return': vpc1_route_table_1_route}))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.destroy()

        logger.debug.assert_any_call(
            "Removing routes from private subnets in: '%s' pointing at "
            "'%s:%s:%s'.",
            vpc1.id, vpc2.id, vpc2.cidr_block, vpc_peering_connection.id)

    def test_logs_that_route_deletion_succeeded(self):
        region_1 = randoms.region()
        region_2 = randoms.region()
        account_id = randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])
        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc1_route_table_1_route = Mock(name="VPC 1 route table 1 route")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[vpc1_route_table_1])

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[])


        ec2_gateway_1.resource().Route = Mock(
            name="Route constructor",
            side_effect=mock_route_for(
                {'arguments': [vpc1_route_table_1.id, vpc2.cidr_block],
                 'return': vpc1_route_table_1_route}))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.destroy()

        logger.debug.assert_any_call(
            "Route deletion succeeded for '%s'. Continuing.",
            vpc1_route_table_1.id)

    def test_logs_that_route_deletion_failed_and_continues_on_exception(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc1_route_table_1 = Mock(name="VPC 1 route table 1")
        vpc2_route_table_1 = Mock(name="VPC 2 route table 1")

        vpc1_route_table_1_route = Mock(name="VPC 1 route table 1 route")
        vpc2_route_table_1_route = Mock(name="VPC 2 route table 1 route")

        ec2_gateway_1.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_1.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[vpc1_route_table_1])

        ec2_gateway_2.resource().route_tables = Mock(
            name="VPC route tables")
        ec2_gateway_2.resource().route_tables.filter = Mock(
            name="Filtered VPC route tables",
            return_value=[vpc2_route_table_1])

        ec2_gateway_1.resource().Route = Mock(
            name="Route constructor",
            side_effect=mock_route_for(
                {'arguments': [vpc1_route_table_1.id, vpc2.cidr_block],
                 'return': vpc1_route_table_1_route}))
        ec2_gateway_2.resource().Route = Mock(
            name="Route constructor",
            side_effect=mock_route_for(
                {'arguments': [vpc2_route_table_1.id, vpc1.cidr_block],
                 'return': vpc2_route_table_1_route}))

        vpc_peering_connection = Mock(name="VPC peering connection")
        vpc_peering_relationship = Mock()
        vpc_peering_relationship.fetch = Mock(
            return_value=vpc_peering_connection)

        delete_error = ClientError({'Error': {'Code': '123'}}, 'something')
        vpc1_route_table_1_route.delete = Mock(
            side_effect=delete_error)

        vpc_peering_routes = VPCPeeringRoutes(
            vpc1, vpc2, vpc_peering_relationship, ec2_gateways, logger)

        vpc_peering_routes.destroy()

        logger.warn.assert_any_call(
            "Route deletion failed for '%s'. Error was: %s",
            vpc1_route_table_1.id, delete_error)

        vpc2_route_table_1_route.delete.assert_called()
