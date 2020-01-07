import test.randoms as randoms


def sts_assume_role_response_for(**kwargs):
    access_key_id = kwargs.get(
        'access_key_id',
        randoms.temporary_access_key_id())
    secret_access_key = kwargs.get(
        'secret_access_key',
        randoms.secret_access_key())
    session_token = kwargs.get(
        'session_token',
        randoms.session_token())
    expiration = kwargs.get(
        'expiration',
        "2022-01-06T15:29:47Z")

    return {
        'Credentials': {
            'AccessKeyId': access_key_id,
            'SecretAccessKey': secret_access_key,
            'SessionToken': session_token,
            'Expiration': expiration
        }
    }
