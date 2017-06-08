from itertools import repeat

from auto_peering.tag_collection import TagCollection
from auto_peering.vpc_dependency import VPCDependency


class AllVPCs(object):
    def __init__(self, ec2_client):
        self.all_vpcs = list(ec2_client.vpcs.all())

    def find_by_id(self, vpc_id):
        return next(
            vpc
            for vpc in self.all_vpcs
            if vpc.id == vpc_id)

    def find_for_component(self, component):
        return next(
            vpc
            for vpc in self.all_vpcs
            if TagCollection(vpc).find_value('Component') == component)

    def find_dependencies_of(self, vpc):
        tag_collection = TagCollection(vpc)
        dependency_components = tag_collection. \
            find_values('Dependencies')

        return [
            self.find_for_component(component)
            for component in dependency_components
        ]

    def find_dependents_of(self, vpc):
        return [
            dependent_vpc
            for dependent_vpc in self.all_vpcs
            if TagCollection(vpc).find_value('Component')
               in TagCollection(dependent_vpc).find_values('Dependencies')
        ]


class VPCDependencies(object):
    def __init__(self, ec2_client, logger):
        self.ec2_client = ec2_client
        self.logger = logger

    def __vpc_dependency_for(self, source, target):
        return VPCDependency(
            source, target, self.ec2_client, self.logger)

    def resolve_for(self, target_vpc_id):
        all_vpcs = AllVPCs(self.ec2_client)

        target_vpc = all_vpcs.find_by_id(target_vpc_id)
        dependency_vpcs = all_vpcs.find_dependencies_of(target_vpc)
        dependent_vpcs = all_vpcs.find_dependents_of(target_vpc)

        vpc_pairs = list(zip(repeat(target_vpc), dependency_vpcs)) + \
                    list(zip(dependent_vpcs, repeat(target_vpc)))

        vpc_dependencies = [
            self.__vpc_dependency_for(source, target)
            for (source, target)
            in vpc_pairs
        ]

        return frozenset(vpc_dependencies)
