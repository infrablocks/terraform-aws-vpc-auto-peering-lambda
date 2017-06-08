from itertools import repeat

from auto_peering.tag_collection import TagCollection
from auto_peering.vpc_link import VPCLink


class AllVPCs(object):
    def __init__(self, ec2_client):
        self.all_vpcs = [
            self.__with_metadata(vpc)
            for vpc in ec2_client.vpcs.all()
        ]

    @staticmethod
    def __with_metadata(vpc):
        vpc.component = TagCollection(vpc).find_value('Component')
        vpc.dependencies = TagCollection(vpc).find_values('Dependencies')
        return vpc

    def find_by_id(self, vpc_id):
        return next(
            (vpc
             for vpc in self.all_vpcs
             if vpc.id == vpc_id),
            None)

    def find_for_component(self, component):
        return next(
            (vpc
             for vpc in self.all_vpcs
             if vpc.component == component),
            None)

    def find_dependencies_of(self, vpc):
        return [
            dependency_vpc
            for dependency_vpc
            in (self.find_for_component(component)
                for component in vpc.dependencies)
            if dependency_vpc is not None
        ]

    def find_dependents_of(self, vpc):
        return [
            dependent_vpc
            for dependent_vpc in self.all_vpcs
            if vpc.component in dependent_vpc.dependencies
        ]


class VPCLinks(object):
    def __init__(self, ec2_client, logger):
        self.ec2_client = ec2_client
        self.logger = logger

    def __vpc_dependency_for(self, source, target):
        return VPCLink(
            source, target, self.ec2_client, self.logger)

    def resolve_for(self, target_vpc_id):
        self.logger.debug(
            "Computing VPC links for VPC with ID: '%s'.",
            target_vpc_id)
        all_vpcs = AllVPCs(self.ec2_client)

        target_vpc = all_vpcs.find_by_id(target_vpc_id)
        if target_vpc:
            self.logger.debug(
                "Found target VPC with ID: '%s', component: '%s' "
                "and dependencies: '%s'.",
                target_vpc_id,
                target_vpc.component,
                target_vpc.dependencies)
        else:
            self.logger.debug(
                "No VPC found with ID: '%s'. Aborting.", target_vpc_id)
            return frozenset()

        dependency_vpcs = all_vpcs.find_dependencies_of(target_vpc)
        self.logger.debug(
            "Found dependency VPCs: [%s]",
            ', '.join([
                "'{}':'{}'".format(
                    dependency_vpc.component,
                    dependency_vpc.id)
                for dependency_vpc in dependency_vpcs]))

        dependent_vpcs = all_vpcs.find_dependents_of(target_vpc)
        self.logger.debug(
            "Found dependent VPCs: [%s]",
            ', '.join([
                "'{}':'{}'".format(
                    dependent_vpc.component,
                    dependent_vpc.id)
                for dependent_vpc in dependent_vpcs]))

        vpc_pairs = list(zip(repeat(target_vpc), dependency_vpcs)) + \
                    list(zip(dependent_vpcs, repeat(target_vpc)))

        vpc_dependencies = [
            self.__vpc_dependency_for(source, target)
            for (source, target)
            in vpc_pairs
        ]

        return frozenset(vpc_dependencies)
