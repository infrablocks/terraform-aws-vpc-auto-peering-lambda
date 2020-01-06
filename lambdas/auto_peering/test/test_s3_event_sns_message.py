import unittest
import json

from auto_peering.s3_event_sns_message import S3EventSNSMessage


def s3_event_for(event_name, key):
    return {'Records': [
        {'eventName': event_name, 's3': {'object': {'key': key}}}
    ]}


def sns_message_containing(s3_event):
    return {'Records': [{'Sns': {'Message': json.dumps(s3_event)}}]}


class TestS3EventSNSMessage(unittest.TestCase):
    def test_has_action_create_when_event_represents_create(self):
        event = sns_message_containing(
            s3_event_for('ObjectCreated:Put',
                         'vpc-existence/111122223333/vpc-4e1ed427'))

        message = S3EventSNSMessage(event)

        self.assertEqual(message.action(), 'provision')

    def test_has_action_destroy_when_event_represents_destroy(self):
        event = sns_message_containing(
            s3_event_for('ObjectRemoved:Delete',
                         'vpc-existence/111122223333/vpc-4e1ed427'))

        message = S3EventSNSMessage(event)

        self.assertEqual(message.action(), 'destroy')

    def test_has_action_unknown_when_event_name_is_not_recognised(self):
        event = sns_message_containing(
            s3_event_for('ReducedRedundancyLostObject',
                         'vpc-created/111122223333/vpc-4e1ed427'))

        message = S3EventSNSMessage(event)

        self.assertEqual(message.action(), 'unknown')

    def test_has_type_extracted_from_object_key(self):
        event = sns_message_containing(
            s3_event_for('ObjectCreated:Put',
                         'vpc-existence/111122223333/vpc-4e1ed427'))

        message = S3EventSNSMessage(event)

        self.assertEqual(message.type(), 'vpc-existence')

    def test_has_account_id_extracted_from_object_key(self):
        event = sns_message_containing(
            s3_event_for('ObjectCreated:Put',
                         'vpc-existence/111122223333/vpc-4e1ed427'))

        message = S3EventSNSMessage(event)

        self.assertEqual(message.account_id(), '111122223333')

    def test_has_vpc_id_extracted_from_object_key(self):
        event = sns_message_containing(
            s3_event_for('ObjectCreated:Put',
                         'vpc-existence/111122223333/vpc-4e1ed427'))

        message = S3EventSNSMessage(event)

        self.assertEqual(message.vpc_id(), 'vpc-4e1ed427')


if __name__ == '__main__':
    unittest.main()
