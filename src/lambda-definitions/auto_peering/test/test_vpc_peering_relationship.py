import unittest
from unittest.mock import Mock
from botocore.exceptions import ClientError

from auto_peering.vpc_peering_relationship import VPCPeeringRelationship


class TestVPCPeeringRelationshipFetch(unittest.TestCase):
    def test_finds_peering_connection_between_first_and_second_vpc(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)

        found_peering_connection = vpc_peering_relationship.fetch()

        vpc_peering_connections.filter.assert_called_with(
            Filters=[
                {'Name': 'accepter-vpc-info.vpc-id',
                 'Values': [vpc1.id]},
                {'Name': 'requester-vpc-info.vpc-id',
                 'Values': [vpc2.id]}])
        self.assertEqual(
            found_peering_connection, matching_vpc_peering_connection)

    def test_finds_peering_connection_between_second_and_first_vpc(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        def conditionally_return_peering_connection(**filters):
            vpc1_to_vpc2_filters = {
                'Filters': [
                    {'Name': 'accepter-vpc-info.vpc-id',
                     'Values': [vpc1.id]},
                    {'Name': 'requester-vpc-info.vpc-id',
                     'Values': [vpc2.id]}]}

            vpc2_to_vpc1_filters = {
                'Filters': [
                    {'Name': 'accepter-vpc-info.vpc-id',
                     'Values': [vpc2.id]},
                    {'Name': 'requester-vpc-info.vpc-id',
                     'Values': [vpc1.id]}]}

            if filters == vpc1_to_vpc2_filters:
                return iter([])

            if filters == vpc2_to_vpc1_filters:
                return iter([matching_vpc_peering_connection])

            raise Exception()

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            side_effect=conditionally_return_peering_connection)

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)

        found_peering_connection = vpc_peering_relationship.fetch()

        vpc_peering_connections.filter.assert_called_with(
            Filters=[
                {'Name': 'accepter-vpc-info.vpc-id',
                 'Values': [vpc2.id]},
                {'Name': 'requester-vpc-info.vpc-id',
                 'Values': [vpc1.id]}])
        self.assertEqual(
            found_peering_connection, matching_vpc_peering_connection)

    def test_returns_none_when_no_peering_connection_exists(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)

        found_peering_connection = vpc_peering_relationship.fetch()

        self.assertIsNone(found_peering_connection)


class TestVPCPeeringRelationshipProvision(unittest.TestCase):
    def test_requests_and_accepts_a_peering_connection(self):
        vpc1 = Mock()
        vpc2 = Mock()
        ec2_client = Mock()
        logger = Mock()

        peering_connection = Mock()
        vpc1.request_vpc_peering_connection = Mock(
            return_value=peering_connection)

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.provision()

        vpc1.request_vpc_peering_connection. \
            assert_called_with(PeerVpcId=vpc2.id)
        peering_connection.accept. \
            assert_called()

    def test_logs_that_peering_connection_is_being_requested(self):
        vpc1 = Mock()
        vpc2 = Mock()
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.provision()

        logger.debug.assert_any_call(
            "Requesting peering connection between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)

    def test_logs_that_peering_connection_is_being_accepted(self):
        vpc1 = Mock()
        vpc2 = Mock()
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.provision()

        logger.debug.assert_any_call(
            "Accepting peering connection between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)

    def test_deletes_created_peering_connection_on_exception(self):
        vpc1 = Mock()
        vpc2 = Mock()
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connection = Mock()
        vpc1.request_vpc_peering_connection = Mock(
            return_value=vpc_peering_connection)
        vpc_peering_connection.accept = Mock(
            side_effect=ClientError({'Error': {'Code': '123'}}, 'something'))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.provision()

        vpc_peering_connection.delete.assert_called()

    def test_logs_that_accepting_peering_connection_failed(self):
        vpc1 = Mock()
        vpc2 = Mock()
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connection = Mock()
        vpc1.request_vpc_peering_connection = Mock(
            return_value=vpc_peering_connection)
        vpc_peering_connection.accept = Mock(
            side_effect=ClientError({'Error': {'Code': '123'}}, 'something'))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.provision()

        logger.warn.assert_any_call(
            "Could not accept peering connection. This may be because one "
            "already exists between '%s' and: '%s'. Continuing.",
            vpc1.id, vpc2.id)


class TestVPCPeeringRelationshipDestroy(unittest.TestCase):
    def test_destroys_peering_connection(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.destroy()

        matching_vpc_peering_connection.delete.assert_called()

    def test_logs_that_peering_connection_is_deleted(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.destroy()

        logger.debug.assert_any_call(
            "Destroying peering connection between: '%s' and: '%s'",
            matching_vpc_peering_connection.requester_vpc.id,
            matching_vpc_peering_connection.accepter_vpc.id)

    def test_does_not_throw_exception_when_no_peering_connection_found(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)

        try:
            vpc_peering_relationship.destroy()
        except Exception as exception:
            self.fail("Expected no exception but got: {0}".format(exception))

    def test_logs_when_no_peering_connection_found(self):
        vpc1 = Mock(name='VPC 1')
        vpc2 = Mock(name='VPC 2')
        ec2_client = Mock()
        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_client.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_client, logger)
        vpc_peering_relationship.destroy()

        logger.debug.assert_any_call(
            "No peering connection to destroy between: '%s' and: '%s'",
            vpc1.id,
            vpc2.id)
