import unittest
import unittest.mock as mock

from auto_peering.session_store import SessionStore

from test import mocks, randoms, builders


class TestSessionStore(unittest.TestCase):
    def test_creates_session_for_provided_account_id(self):
        sts_client = mocks.build_sts_client_mock()
        peering_role_name = randoms.role_name()
        account_id = randoms.account_id()

        expected_credentials, assume_role_mock = \
            mocks.build_sts_assume_role_mock()

        sts_client.assume_role = assume_role_mock

        session_store = SessionStore(sts_client, peering_role_name)

        session = session_store.get_session_for(account_id)

        assume_role_call = sts_client.assume_role.call_args

        expected_role_arn = \
            builders.build_role_arn_for(account_id, peering_role_name)
        expected_role_session_name = "VPC Auto Peering Lambda"

        self.assertEqual(len(sts_client.assume_role.mock_calls), 1)
        self.assertEqual(
            assume_role_call,
            mock.call(
                RoleArn=expected_role_arn,
                RoleSessionName=expected_role_session_name))

        actual_credentials = session.get_credentials()

        self.assertEqual(
            actual_credentials.access_key,
            expected_credentials.access_key)
        self.assertEqual(
            actual_credentials.secret_key,
            expected_credentials.secret_key)
        self.assertEqual(
            actual_credentials.token,
            expected_credentials.token)

    def test_caches_session_for_account_id(self):
        sts_client = mocks.build_sts_client_mock()
        peering_role_name = randoms.role_name()
        account_id = randoms.account_id()

        expected_credentials, assume_role_mock = \
            mocks.build_sts_assume_role_mock()

        sts_client.assume_role = assume_role_mock

        session_store = SessionStore(sts_client, peering_role_name)

        first_session = session_store.get_session_for(account_id)
        second_session = session_store.get_session_for(account_id)

        self.assertEqual(len(sts_client.assume_role.mock_calls), 1)
        self.assertEqual(first_session, second_session)
