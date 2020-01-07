from test import randoms


def build_role_arn_for(account_id, role_name):
    return "arn:aws:iam::%s:role/%s" % (account_id, role_name)


def build_vpc_tags(**kwargs):
    return [
        {
            'Key': 'Component',
            'Value': kwargs.get('component', randoms.component())
        },
        {
            'Key': 'DeploymentIdentifier',
            'Value': kwargs.get('deployment_identifier',
                                randoms.deployment_identifier())
        },
        {
            'Key': 'Dependencies',
            'Value': ','.join(kwargs.get('dependencies',
                                         randoms.dependencies()))
        }
    ]
