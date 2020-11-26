from auto_peering.all_vpcs import AllVPCs
from auto_peering.vpc_link import VPCLink


class VPCLinks(object):
    def __init__(self, ec2_gateways, logger):
        self.ec2_gateways = ec2_gateways
        self.all_vpcs = AllVPCs(self.ec2_gateways)
        self.logger = logger

    def __vpc_link(self, between, routes):
        return VPCLink(self.ec2_gateways, self.logger, between, routes)

    def resolve_for(self, target_account_id, target_vpc_id):
        self.logger.info(
            "Computing VPC links for VPC with ID: '%s' " 
            "in account with ID: '%s'.",
            target_vpc_id,
            target_account_id)

        target_vpc = \
            self.all_vpcs.find_by_account_id_and_vpc_id(
                target_account_id, target_vpc_id)
        if target_vpc:
            self.logger.info(
                "Found target VPC with ID: '%s', component: '%s', "
                "deployment identifier: '%s' and dependencies: '%s'.",
                target_vpc_id,
                target_vpc.component,
                target_vpc.deployment_identifier,
                target_vpc.dependencies)
        else:
            self.logger.info(
                "No VPC found with ID: '%s'. Aborting.", target_vpc_id)
            return frozenset()

        dependency_vpcs = self.all_vpcs.find_dependencies_of(target_vpc)
        self.logger.info(
            "Found dependency VPCs: [%s]",
            ', '.join([
                "'{}':'{}'".format(
                    dependency_vpc.component_instance_identifier,
                    dependency_vpc.id)
                for dependency_vpc in dependency_vpcs]))

        dependent_vpcs = self.all_vpcs.find_dependents_of(target_vpc)
        self.logger.info(
            "Found dependent VPCs: [%s]",
            ', '.join([
                "'{}':'{}'".format(
                    dependent_vpc.component_instance_identifier,
                    dependent_vpc.id)
                for dependent_vpc in dependent_vpcs]))

        bidirectional_vpc_links = [
            self.__vpc_link(
                between=[target_vpc, dependency_vpc],
                routes=[[target_vpc, dependency_vpc],
                        [dependency_vpc, target_vpc]])
            for dependency_vpc
            in dependency_vpcs
            if dependency_vpc in dependent_vpcs
        ]
        dependency_only_vpc_links = [
            self.__vpc_link(
                between=[target_vpc, dependency_vpc],
                routes=[[target_vpc, dependency_vpc]])
            for dependency_vpc
            in dependency_vpcs
            if dependency_vpc not in dependent_vpcs
        ]
        dependent_only_vpc_links = [
            self.__vpc_link(
                between=[dependent_vpc, target_vpc],
                routes=[[dependent_vpc, target_vpc]])
            for dependent_vpc
            in dependent_vpcs
            if dependent_vpc not in dependency_vpcs
        ]

        vpc_links = \
            bidirectional_vpc_links + \
            dependency_only_vpc_links + \
            dependent_only_vpc_links

        return frozenset(vpc_links)
