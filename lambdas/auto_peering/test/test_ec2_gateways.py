import unittest
from unittest import mock

from auto_peering.ec2_gateway import EC2Gateway
from auto_peering.ec2_gateways import EC2Gateways

from test import randoms


class TestEC2Gateways(unittest.TestCase):
    def test_fetches_all_ec2_gateways(self):
        session_store = mock.Mock(name="SessionStore")

        account_1_id = randoms.account_id()
        account_2_id = randoms.account_id()

        region_1 = randoms.region()
        region_2 = randoms.region()

        account_1_session = mock.Mock(name="Session for account 1")
        account_2_session = mock.Mock(name="Session for account 2")

        def get_session(account_id):
            return {
                account_1_id: account_1_session,
                account_2_id: account_2_session
            }[account_id]

        session_store.get_session_for = mock.Mock(
            name="SessionStore#get_session_for",
            side_effect=get_session)

        account_ids = [account_1_id, account_2_id]
        regions = [region_1, region_2]

        ec2_gateways = EC2Gateways(session_store, account_ids, regions)

        ec2_gateway_instances = ec2_gateways.all()

        self.assertEqual(
            set(ec2_gateway_instances),
            {EC2Gateway(account_1_session, account_1_id, region_1),
             EC2Gateway(account_1_session, account_1_id, region_2),
             EC2Gateway(account_2_session, account_2_id, region_1),
             EC2Gateway(account_2_session, account_2_id, region_2)})

    def test_fetches_ec2_gateways_for_provided_account(self):
        session_store = mock.Mock(name="SessionStore")

        account_1_id = randoms.account_id()
        account_2_id = randoms.account_id()

        region_1 = randoms.region()
        region_2 = randoms.region()

        account_1_session = mock.Mock(name="Session for account 1")
        account_2_session = mock.Mock(name="Session for account 2")

        def get_session(account_id):
            return {
                account_1_id: account_1_session,
                account_2_id: account_2_session
            }[account_id]

        session_store.get_session_for = mock.Mock(
            name="SessionStore#get_session_for",
            side_effect=get_session)

        account_ids = [account_1_id, account_2_id]
        regions = [region_1, region_2]

        ec2_gateways = EC2Gateways(session_store, account_ids, regions)

        ec2_gateway_instances = ec2_gateways.by_account_id(account_2_id)

        self.assertEqual(
            set(ec2_gateway_instances),
            {EC2Gateway(account_2_session, account_2_id, region_1),
             EC2Gateway(account_2_session, account_2_id, region_2)})

    def test_fetches_ec2_gateway_for_provided_account_and_region(self):
        session_store = mock.Mock(name="SessionStore")

        account_id = randoms.account_id()
        region = randoms.region()
        session = mock.Mock(name="Session for account 1")

        session_store.get_session_for = mock.Mock(
            name="SessionStore#get_session_for",
            return_value=session)

        ec2_gateways = EC2Gateways(session_store, [account_id], [region])

        ec2_gateway_instance = \
            ec2_gateways.by_account_id_and_region(account_id, region)

        self.assertEqual(
            ec2_gateway_instance,
            EC2Gateway(session, account_id, region))
