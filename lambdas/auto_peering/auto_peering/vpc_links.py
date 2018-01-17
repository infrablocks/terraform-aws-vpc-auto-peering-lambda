from itertools import repeat
from functools import reduce

from auto_peering.tag_collection import TagCollection
from auto_peering.vpc_link import VPCLink


class AllVPCs(object):
    def __init__(self, ec2_resources):
        self.all_vpcs = reduce(
            lambda x, y: x + y,
            [[self.__with_metadata(vpc, region)
              for vpc in ec2_resource.vpcs.all()]
             for region, ec2_resource in ec2_resources.items()])

    @staticmethod
    def __with_metadata(vpc, region):
        vpc.region = region
        vpc.component = \
            TagCollection(vpc).find_value('Component')
        vpc.deployment_identifier = \
            TagCollection(vpc).find_value('DeploymentIdentifier')
        vpc.dependencies = \
            TagCollection(vpc).find_values('Dependencies')
        vpc.identifier = \
            "{}-{}".format(vpc.component, vpc.deployment_identifier)
        return vpc

    def find_by_id(self, vpc_id):
        return next(
            (vpc
             for vpc in self.all_vpcs
             if vpc.id == vpc_id),
            None)

    def find_for_identifier(self, identifier):
        return next(
            (vpc
             for vpc in self.all_vpcs
             if vpc.identifier == identifier),
            None)

    def find_dependencies_of(self, vpc):
        return [
            dependency_vpc
            for dependency_vpc
            in (self.find_for_identifier(identifier)
                for identifier in vpc.dependencies)
            if dependency_vpc is not None
        ]

    def find_dependents_of(self, vpc):
        return [
            dependent_vpc
            for dependent_vpc in self.all_vpcs
            if vpc.identifier in dependent_vpc.dependencies
        ]


class VPCLinks(object):
    def __init__(self, ec2_resources, logger):
        self.ec2_resources = ec2_resources
        self.logger = logger

    def __vpc_link_for(self, source, target):
        return VPCLink(
            source, target, self.ec2_resources, self.logger)

    def resolve_for(self, target_vpc_id):
        self.logger.debug(
            "Computing VPC links for VPC with ID: '%s'.",
            target_vpc_id)
        all_vpcs = AllVPCs(self.ec2_resources)

        target_vpc = all_vpcs.find_by_id(target_vpc_id)
        if target_vpc:
            self.logger.debug(
                "Found target VPC with ID: '%s', component: '%s', "
                "deployment identifier: '%s' and dependencies: '%s'.",
                target_vpc_id,
                target_vpc.component,
                target_vpc.deployment_identifier,
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
                    dependency_vpc.identifier,
                    dependency_vpc.id)
                for dependency_vpc in dependency_vpcs]))

        dependent_vpcs = all_vpcs.find_dependents_of(target_vpc)
        self.logger.debug(
            "Found dependent VPCs: [%s]",
            ', '.join([
                "'{}':'{}'".format(
                    dependent_vpc.identifier,
                    dependent_vpc.id)
                for dependent_vpc in dependent_vpcs]))

        vpc_pairs = list(zip(repeat(target_vpc), dependency_vpcs)) + \
                    list(zip(dependent_vpcs, repeat(target_vpc)))

        vpc_links = [
            self.__vpc_link_for(source, target)
            for (source, target)
            in vpc_pairs
        ]

        return frozenset(vpc_links)
