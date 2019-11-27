import unittest
from unittest.mock import Mock, PropertyMock
from botocore.exceptions import ClientError

from auto_peering.ec2_gateway import EC2Gateway
from auto_peering.vpc_peering_relationship import VPCPeeringRelationship


class TestVPCPeeringRelationshipFetch(unittest.TestCase):
    def test_finds_peering_connection_between_first_and_second_vpc(self):
        region_1 = 'eu-west-1'
        region_2 = 'eu-west-2'

        vpc_1 = Mock(name='VPC 1')
        type(vpc_1).region = PropertyMock(return_value=region_1)
        vpc_2 = Mock(name='VPC 2')
        type(vpc_2).region = PropertyMock(return_value=region_2)

        ec2_resource_1 = Mock(name='EC2 resource')
        ec2_client_1 = Mock(name='EC2 client')
        ec2_resource_2 = Mock(name='EC2 resource')
        ec2_client_2 = Mock(name='EC2 client')

        ec2_gateways = {
            region_1: EC2Gateway(ec2_resource_1, ec2_client_1, region_1),
            region_2: EC2Gateway(ec2_resource_2, ec2_client_2, region_2),
        }

        logger = Mock()

        vpc_peering_connections_1 = Mock(
            name='VPC peering connections for region: {}'.format(region_1))
        vpc_peering_connections_2 = Mock(
            name='VPC peering connections for region: {}'.format(region_2))
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_resource_1.vpc_peering_connections = vpc_peering_connections_1
        vpc_peering_connections_1.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_1),
            return_value=iter([matching_vpc_peering_connection]))

        ec2_resource_2.vpc_peering_connections = vpc_peering_connections_2
        vpc_peering_connections_2.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_2),
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc_1, vpc_2, ec2_gateways, logger)

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
        region_1 = 'eu-west-1'
        region_2 = 'eu-west-2'

        vpc_1 = Mock(name='VPC 1')
        type(vpc_1).region = PropertyMock(return_value=region_1)
        vpc_2 = Mock(name='VPC 2')
        type(vpc_2).region = PropertyMock(return_value=region_2)

        ec2_resource_1 = Mock(name='EC2 resource')
        ec2_client_1 = Mock(name='EC2 client')
        ec2_resource_2 = Mock(name='EC2 resource')
        ec2_client_2 = Mock(name='EC2 client')

        ec2_gateways = {
            region_1: EC2Gateway(ec2_resource_1, ec2_client_1, region_1),
            region_2: EC2Gateway(ec2_resource_2, ec2_client_2, region_2),
        }

        logger = Mock()

        vpc_peering_connections_1 = Mock(
            name='VPC peering connections for region: {}'.format(region_1))
        vpc_peering_connections_2 = Mock(
            name='VPC peering connections for region: {}'.format(region_2))
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_resource_1.vpc_peering_connections = vpc_peering_connections_1
        vpc_peering_connections_1.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_1),
            return_value=iter([]))

        ec2_resource_2.vpc_peering_connections = vpc_peering_connections_2
        vpc_peering_connections_2.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region_2),
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc_1, vpc_2, ec2_gateways, logger)

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
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)

        found_peering_connection = vpc_peering_relationship.fetch()

        self.assertIsNone(found_peering_connection)


class TestVPCPeeringRelationshipProvision(unittest.TestCase):
    def test_requests_and_accepts_a_peering_connection(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        peering_connection = Mock()
        vpc1.request_vpc_peering_connection = Mock(
            return_value=peering_connection)

        vpc_peering_connections = Mock(
            name='VPC peering connections for region: {}'.format(region))
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections for region: {}". \
                format(region),
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.provision()

        vpc1.request_vpc_peering_connection. \
            assert_called_with(PeerVpcId=vpc2.id, PeerRegion=region)
        matching_vpc_peering_connection.accept. \
            assert_called()

    def test_logs_that_peering_connection_is_being_requested(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.provision()

        logger.debug.assert_any_call(
            "Requesting peering connection between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)

    def test_logs_that_peering_connection_is_being_accepted(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.provision()

        logger.debug.assert_any_call(
            "Accepting peering connection between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)

    def test_deletes_created_peering_connection_on_exception(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')
        vpc_peering_connection.delete = \
            Mock(name='Delete VPC peering connection')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        vpc1.request_vpc_peering_connection = Mock(
            return_value=vpc_peering_connection)
        vpc_peering_connection.accept = Mock(
            side_effect=ClientError({'Error': {'Code': '123'}}, 'something'))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.provision()

        vpc_peering_connection.delete.assert_called()

    def test_logs_that_accepting_peering_connection_failed(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        vpc_peering_connection = Mock(name='VPC peering connection')

        vpc_peering_connection.id = Mock(name='VPC peering connection ID')
        vpc_peering_connection.delete = \
            Mock(name='Delete VPC peering connection')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([vpc_peering_connection]))

        accept_error = ClientError({'Error': {'Code': '123'}}, 'something')
        vpc1.request_vpc_peering_connection = Mock(
            return_value=vpc_peering_connection)
        vpc_peering_connection.accept = Mock(
            side_effect=accept_error)

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.provision()

        logger.warn.assert_any_call(
            "Could not accept peering connection between: '%s' and: '%s'. "
            "Error was: %s",
            vpc1.id, vpc2.id, accept_error)


class TestVPCPeeringRelationshipDestroy(unittest.TestCase):
    def test_destroys_peering_connection(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.destroy()

        matching_vpc_peering_connection.delete.assert_called()

    def test_logs_that_peering_connection_is_deleted(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')
        matching_vpc_peering_connection = Mock(
            name='Matching VPC peering connection')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([matching_vpc_peering_connection]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.destroy()

        logger.debug.assert_any_call(
            "Destroying peering connection between: '%s' and: '%s'.",
            matching_vpc_peering_connection.requester_vpc.id,
            matching_vpc_peering_connection.accepter_vpc.id)

    def test_does_not_throw_exception_when_no_peering_connection_found(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)

        try:
            vpc_peering_relationship.destroy()
        except Exception as exception:
            self.fail("Expected no exception but got: {0}".format(exception))

    def test_logs_when_no_peering_connection_found(self):
        region = 'eu-west-1'

        vpc1 = Mock(name='VPC 1')
        type(vpc1).region = PropertyMock(return_value=region)
        vpc2 = Mock(name='VPC 2')
        type(vpc2).region = PropertyMock(return_value=region)

        ec2_resource = Mock(name='EC2 resource')
        ec2_client = Mock(name='EC2 client')
        ec2_gateway = EC2Gateway(ec2_resource, ec2_client, region)
        ec2_gateways = {region: ec2_gateway}

        logger = Mock()

        vpc_peering_connections = Mock(name='VPC peering connections')

        ec2_resource.vpc_peering_connections = vpc_peering_connections
        vpc_peering_connections.filter = Mock(
            name="Filter VPC peering connections",
            return_value=iter([]))

        vpc_peering_relationship = VPCPeeringRelationship(
            vpc1, vpc2, ec2_gateways, logger)
        vpc_peering_relationship.destroy()

        logger.debug.assert_any_call(
            "No peering connection to destroy between: '%s' and: '%s'.",
            vpc1.id, vpc2.id)
