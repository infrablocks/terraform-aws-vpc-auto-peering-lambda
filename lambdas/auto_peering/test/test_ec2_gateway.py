import unittest
import unittest.mock as mock

from auto_peering.ec2_gateway import EC2Gateway

from test import randoms


class TestEC2Gateway(unittest.TestCase):
    def test_returns_ec2_client_for_region_from_session(self):
        session = mock.Mock(name='Session')
        account_id = randoms.account_id()
        region = randoms.region()

        expected_client = mock.Mock(name='EC2 Client')
        session.client = mock.Mock(
            name='Client',
            return_value=expected_client)

        ec2_gateway = EC2Gateway(session, account_id, region)

        actual_client = ec2_gateway.client()

        session_client_calls = session.client.mock_calls
        self.assertEqual(len(session_client_calls), 1)

        session_client_call = session_client_calls[0]
        self.assertEqual(
            session_client_call,
            mock.call('ec2', region))

        self.assertEqual(actual_client, expected_client)

    def test_returns_ec2_resource_for_region_from_session(self):
        session = mock.Mock(name='Session')
        account_id = randoms.account_id()
        region = randoms.region()

        expected_resource = mock.Mock(name='EC2 Resource')
        session.resource = mock.Mock(
            name='Resource',
            return_value=expected_resource)

        ec2_gateway = EC2Gateway(session, account_id, region)

        actual_resource = ec2_gateway.resource()

        session_resource_calls = session.resource.mock_calls
        self.assertEqual(len(session_resource_calls), 1)

        session_resource_call = session_resource_calls[0]
        self.assertEqual(
            session_resource_call,
            mock.call('ec2', region))

        self.assertEqual(actual_resource, expected_resource)
