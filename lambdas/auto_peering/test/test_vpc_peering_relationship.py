import unittest
from unittest.mock import Mock
from botocore.exceptions import ClientError

from auto_peering.vpc import VPC
from auto_peering.vpc_peering_relationship import VPCPeeringRelationship
from test import randoms, mocks


class TestVPCPeeringRelationshipFetch(unittest.TestCase):
    def test_finds_peering_connection_between_first_and_second_vpc(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc_1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc_2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc_peering_connections_1 = Mock(
            name='VPC peering connections for region: {}'.format(region_1))
        vpc_peering_connections_2 = Mock(
            name='VPC peering connections for region: {}'.format(region_2))
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_gateway_1.resource().vpc_peering_connections = \
            vpc_peering_connections_1
        vpc_peering_connections_1.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_1),
            return_value=iter([matching_vpc_peering_connection]))

        ec2_gateway_2.resource().vpc_peering_connections = \
            vpc_peering_connections_2
        vpc_peering_connections_2.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_2),
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc_1, vpc_2])

        found_peering_connection = vpc_peering_relationship.fetch()

        vpc_peering_connections_1.filter.assert_called_with(
            Filters=[
                {'Name': 'accepter-vpc-info.vpc-id',
                 'Values': [vpc_1.id]},
                {'Name': 'requester-vpc-info.vpc-id',
                 'Values': [vpc_2.id]}])
        self.assertEqual(
            found_peering_connection, matching_vpc_peering_connection)

    def test_finds_peering_connection_between_second_and_first_vpc(self):
        account_id = randoms.account_id()
        region_1 = randoms.region()
        region_2 = randoms.region()

        vpc_1 = VPC(mocks.build_vpc_response_mock(), account_id, region_1)
        vpc_2 = VPC(mocks.build_vpc_response_mock(), account_id, region_2)

        ec2_gateway_1 = mocks.EC2Gateway(account_id, region_1)
        ec2_gateway_2 = mocks.EC2Gateway(account_id, region_2)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway_1, ec2_gateway_2])

        logger = Mock()

        vpc_peering_connections_1 = Mock(
            name='VPC peering connections for region: {}'.format(region_1))
        vpc_peering_connections_2 = Mock(
            name='VPC peering connections for region: {}'.format(region_2))
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_gateway_1.resource().vpc_peering_connections = vpc_peering_connections_1
        vpc_peering_connections_1.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_1),
            return_value=iter([]))

        ec2_gateway_2.resource().vpc_peering_connections = vpc_peering_connections_2
        vpc_peering_connections_2.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_2),
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc_1, vpc_2])

        found_peering_connection = vpc_peering_relationship.fetch()

        vpc_peering_connections_2.filter.assert_called_with(
            Filters=[
                {'Name': 'accepter-vpc-info.vpc-id',
                 'Values': [vpc_2.id]},
                {'Name': 'requester-vpc-info.vpc-id',
                 'Values': [vpc_1.id]}])
        self.assertEqual(
            found_peering_connection, matching_vpc_peering_connection)

    def test_returns_none_when_no_peering_connection_exists(self):
        account_id = randoms.account_id()
        region = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])

        found_peering_connection = vpc_peering_relationship.fetch()

        self.assertIsNone(found_peering_connection)


class TestVPCPeeringRelationshipProvision(unittest.TestCase):
    def test_requests_and_accepts_a_peering_connection(self):
        requester_account_id = mocks.randoms.account_id()
        accepter_account_id = mocks.randoms.account_id()
        region = mocks.randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), requester_account_id,
                   region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), accepter_account_id, region)

        requester_ec2_gateway = mocks.EC2Gateway(requester_account_id, region)
        accepter_ec2_gateway = mocks.EC2Gateway(accepter_account_id, region)
        ec2_gateways = mocks.EC2Gateways(
            [requester_ec2_gateway, accepter_ec2_gateway])

        logger = Mock()

        peering_connection = Mock()
        vpc1.request_vpc_peering_connection = Mock(
            return_value=peering_connection)

        vpc_peering_connections = Mock(
            name='VPC peering connections for region: {}'.format(region))
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        accepter_ec2_gateway.resource().vpc_peering_connections = \
            vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections for region: {}".format(region),
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.provision()

        vpc1.request_vpc_peering_connection. \
            assert_called_with(
            PeerOwnerId=accepter_account_id,
            PeerVpcId=vpc2.id,
            PeerRegion=region)
        matching_vpc_peering_connection.accept. \
            assert_called()

    def test_logs_that_peering_connection_is_being_requested(self):
        account_id = mocks.randoms.account_id()
        region = mocks.randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.provision()

        logger.info.assert_any_call(
            "Requesting peering connection between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)

    def test_logs_that_peering_connection_is_being_accepted(self):
        account_id = mocks.randoms.account_id()
        region = mocks.randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.provision()

        logger.info.assert_any_call(
            "Accepting peering connection between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)

    def test_deletes_created_peering_connection_on_exception(self):
        region = mocks.randoms.region()
        account_id = mocks.randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')
        vpc_peering_connection.delete = \
            Mock(name='Delete VPC peering connection')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        vpc1.request_vpc_peering_connection = Mock(
            return_value=vpc_peering_connection)
        vpc_peering_connection.accept = Mock(
            side_effect=ClientError({'Error': {'Code': '123'}}, 'something'))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.provision()

        vpc_peering_connection.delete.assert_called()

    def test_logs_that_accepting_peering_connection_failed(self):
        region = mocks.randoms.region()
        account_id = mocks.randoms.account_id()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')
        vpc_peering_connection.delete = \
            Mock(name='Delete VPC peering connection')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        accept_error = ClientError({'Error': {'Code': '123'}}, 'something')
        vpc1.request_vpc_peering_connection = Mock(
            return_value=vpc_peering_connection)
        vpc_peering_connection.accept = Mock(
            side_effect=accept_error)

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.provision()

        logger.warn.assert_any_call(
            "Could not accept peering connection between: '%s' and: '%s'. "
            "Error was: %s",
            vpc1.id, vpc2.id, accept_error)


class TestVPCPeeringRelationshipDestroy(unittest.TestCase):
    def test_destroys_peering_connection(self):
        account_id = randoms.account_id()
        region = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.destroy()

        matching_vpc_peering_connection.delete.assert_called()

    def test_logs_that_peering_connection_is_deleted(self):
        account_id = randoms.account_id()
        region = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.destroy()

        logger.info.assert_any_call(
            "Destroying peering connection between: '%s' and: '%s'.",
            matching_vpc_peering_connection.requester_vpc.id,
            matching_vpc_peering_connection.accepter_vpc.id)

    def test_does_not_throw_exception_when_no_peering_connection_found(self):
        account_id = randoms.account_id()
        region = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])

        try:
            vpc_peering_relationship.destroy()
        except Exception as exception:
            self.fail("Expected no exception but got: {0}".format(exception))

    def test_logs_when_no_peering_connection_found(self):
        account_id = randoms.account_id()
        region = randoms.region()

        vpc1 = VPC(mocks.build_vpc_response_mock(), account_id, region)
        vpc2 = VPC(mocks.build_vpc_response_mock(), account_id, region)

        ec2_gateway = mocks.EC2Gateway(account_id, region)
        ec2_gateways = mocks.EC2Gateways([ec2_gateway])

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_gateway.resource().vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            ec2_gateways, logger, between=[vpc1, vpc2])
        vpc_peering_relationship.destroy()

        logger.info.assert_any_call(
            "No peering connection to destroy between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)
