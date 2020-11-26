import random
import string as character_sets
import botocore.credentials as creds


def element(elements):
    return random.choice(elements)


def string(characters, length=20):
    return ''.join(random.choice(characters)
                   for n in range(length))


def alphanumeric_string(length=20):
    return string(
        character_sets.ascii_letters + character_sets.digits,
        length)


def uppercase_alphanumeric_string(length=20):
    return string(
        character_sets.ascii_uppercase + character_sets.digits,
        length)


def hyphenated_lowercase_string(length=20):
    return string(
        character_sets.ascii_lowercase + "-",
        length)


def numeric_string(length=20):
    return string(
        character_sets.digits,
        length)


def region():
    return element([
        "us-east-2",
        "us-east-1",
        "us-west-1",
        "us-west-2",
        "ap-east-1",
        "ap-south-1",
        "ap-northeast-3",
        "ap-northeast-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-northeast-1",
        "ca-central-1",
        "cn-north-1",
        "cn-northwest-1",
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-north-1",
        "me-south-1",
        "sa-east-1"
    ])


def vpc_id():
    return "vpc-%s" % numeric_string(17)


def route_table_id():
    return "rtb-%s" % numeric_string(17)


def peering_connection_id():
    return "pcx-%s" % alphanumeric_string(17)


def role_name():
    return hyphenated_lowercase_string(32)


def account_id():
    return numeric_string(12)


def temporary_access_key_id():
    return 'ASIA%s' % uppercase_alphanumeric_string(length=16)


def secret_access_key():
    return alphanumeric_string(40)


def session_token():
    return '%s==' % alphanumeric_string(342)


def credentials():
    access_key = temporary_access_key_id()
    secret_key = secret_access_key()
    token = session_token()

    return creds.Credentials(
        access_key,
        secret_key,
        token)


def cidr_block():
    return element(['10.0.0.0/24', '10.0.1.0/24', '10.0.2.0/24'])


def component():
    return hyphenated_lowercase_string()


def deployment_identifier():
    return hyphenated_lowercase_string()


def dependencies():
    return [hyphenated_lowercase_string(), hyphenated_lowercase_string()]
