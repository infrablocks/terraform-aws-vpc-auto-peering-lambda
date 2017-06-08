import unittest
from unittest.mock import Mock

from auto_peering.vpc_dependencies import VPCDependencies
from auto_peering.vpc_dependency import VPCDependency


def tags_for(component, dependencies):
    return [
        {'Key': 'Component', 'Value': component},
        {'Key': 'Dependencies', 'Value': ','.join(dependencies)}
    ]


class TestVPCDependencies(unittest.TestCase):
    def test_resolve_dependencies_for_target_vpc(self):
        self.maxDiff = None

        target_vpc_id = "vpc-12345678"

        target_vpc = Mock(name="Target VPC")
        target_vpc.id = target_vpc_id
        target_vpc.tags = tags_for('thing1', ['thing2', 'thing3'])

        dependency_vpc1 = Mock(name="Dependency VPC 1")
        dependency_vpc1.tags = tags_for('thing2', [])
        dependency_vpc2 = Mock(name="Dependency VPC 2")
        dependency_vpc2.tags = tags_for('thing3', [])

        dependent_vpc = Mock(name="Dependent VPC")
        dependent_vpc.tags = tags_for('thing4', ['thing1'])

        other_vpc = Mock(name="Other VPC")
        other_vpc.tags = tags_for('other-thing', [])

        ec2_client = Mock(name="EC2 client")
        logger = Mock(name="Logger")

        ec2_client.vpcs.all = Mock(
            name="All VPCs",
            return_value=iter(
                [target_vpc,
                 dependency_vpc1,
                 dependency_vpc2,
                 dependent_vpc,
                 other_vpc]))

        vpc_dependencies = VPCDependencies(ec2_client, logger)
        resolved_vpc_dependencies = vpc_dependencies. \
            resolve_for(target_vpc_id)

        self.assertEqual(
            resolved_vpc_dependencies,
            [VPCDependency(target_vpc, dependency_vpc1,
                           ec2_client, logger),
             VPCDependency(target_vpc, dependency_vpc2,
                           ec2_client, logger),
             VPCDependency(dependent_vpc, target_vpc,
                           ec2_client, logger)]
        )
