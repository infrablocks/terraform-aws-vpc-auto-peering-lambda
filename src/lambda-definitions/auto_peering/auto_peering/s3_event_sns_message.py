import json
import re


class S3EventSNSMessage(object):
    def __init__(self, event):
        self.event = event

    def __s3_event(self):
        sns_message = self.event['Records'][0]['Sns']['Message']
        s3_event = json.loads(sns_message)['Records'][0]
        return s3_event

    def __s3_event_name(self):
        return self.__s3_event()['eventName']

    def __s3_object_key(self):
        return self.__s3_event()['s3']['object']['key']

    def __s3_object_key_parts(self):
        return self.__s3_object_key().split('/')

    def action(self):
        action = 'unknown'
        if re.compile('ObjectCreated.*').match(self.__s3_event_name()):
            action = 'create'
        if re.compile('ObjectRemoved.*').match(self.__s3_event_name()):
            action = 'destroy'

        return action

    def type(self):
        return self.__s3_object_key_parts()[0]

    def target(self):
        return self.__s3_object_key_parts()[1]
