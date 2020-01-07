from functools import lru_cache

from auto_peering.vpc import VPC


class AllVPCs(object):
    def __init__(self, ec2_gateways):
        self.ec2_gateways = ec2_gateways

    @lru_cache(maxsize=1)
    def find_all(self):
        return [
            VPC(vpc_response,
                ec2_gateway.account_id,
                ec2_gateway.region)
            for ec2_gateway in self.ec2_gateways.all()
            for vpc_response in ec2_gateway.resource().vpcs.all()
        ]

    @lru_cache(maxsize=32)
    def find_by_account_id(self, account_id):
        return [
            VPC(vpc_response,
                ec2_gateway.account_id,
                ec2_gateway.region)
            for ec2_gateway in self.ec2_gateways.by_account_id(account_id)
            for vpc_response in ec2_gateway.resource().vpcs.all()
        ]

    @lru_cache(maxsize=32)
    def find_by_account_id_and_vpc_id(self, account_id, vpc_id):
        return next(
            (vpc
             for vpc in self.find_by_account_id(account_id)
             if vpc.id == vpc_id),
            None)

    @lru_cache(maxsize=32)
    def find_by_component_instance_identifier(self, identifier):
        return next(
            (vpc
             for vpc in self.find_all()
             if vpc.component_instance_identifier == identifier),
            None)

    @lru_cache(maxsize=32)
    def find_dependencies_of(self, vpc):
        return [
            self.find_by_component_instance_identifier(
                component_instance_identifier)
            for component_instance_identifier in vpc.dependencies
            if self.find_by_component_instance_identifier(
                component_instance_identifier) is not None
        ]

    @lru_cache(maxsize=32)
    def find_dependents_of(self, vpc):
        return [
            dependent_vpc
            for dependent_vpc in self.find_all()
            if vpc.component_instance_identifier in dependent_vpc.dependencies
        ]
