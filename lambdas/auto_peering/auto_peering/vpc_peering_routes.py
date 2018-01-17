from botocore.exceptions import ClientError


class VPCPeeringRoutes(object):
    def __init__(self, vpc1, vpc2,
                 vpc_peering_relationship, ec2_resources, logger):
        self.vpc1 = vpc1
        self.vpc2 = vpc2
        self.vpc_peering_relationship = vpc_peering_relationship
        self.ec2_resources = ec2_resources
        self.logger = logger

    def __private_route_tables_for(self, vpc):
        ec2_resource = self.ec2_resources.get(vpc.region)

        return ec2_resource.route_tables.filter(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc.id]},
                {'Name': 'tag:Tier', 'Values': ['private']}])

    def __create_routes_in(self, route_tables, destination_vpc,
                           vpc_peering_connection):
        for route_table in route_tables:
            try:
                route_table.create_route(
                    DestinationCidrBlock=destination_vpc.cidr_block,
                    VpcPeeringConnectionId=vpc_peering_connection.id)
                self.logger.debug(
                    "Route creation succeeded for '%s'. Continuing.",
                    route_table.id)
            except ClientError:
                self.logger.warn(
                    "Route creation failed for '%s'. It may already exist. "
                    "Continuing.",
                    route_table.id)

    def __create_routes_for(self, source_vpc, destination_vpc,
                            vpc_peering_connection):
        self.logger.debug(
            "Adding routes to private subnets in: '%s' pointing at '%s:%s:%s'.",
            source_vpc.id, destination_vpc.id, destination_vpc.cidr_block,
            vpc_peering_connection.id)

        self.__create_routes_in(
            self.__private_route_tables_for(source_vpc),
            destination_vpc, vpc_peering_connection)

    def __delete_routes_in(self, route_tables, source_vpc, destination_vpc):
        for route_table in route_tables:
            try:
                ec2_resource = self.ec2_resources.get(source_vpc.region)
                route = ec2_resource.Route(
                    route_table.id, destination_vpc.cidr_block)
                route.delete()
                self.logger.debug(
                    "Route deletion succeeded for '%s'. Continuing.",
                    route_table.id)
            except ClientError:
                self.logger.warn(
                    "Route deletion failed for '%s'. It may have already been "
                    "deleted. Continuing.",
                    route_table.id)

    def __delete_routes_for(self, source_vpc, destination_vpc,
                            vpc_peering_connection):
        self.logger.debug(
            "Removing routes from private subnets in: '%s' pointing at "
            "'%s:%s:%s'.",
            source_vpc.id, destination_vpc.id, destination_vpc.cidr_block,
            vpc_peering_connection.id)

        self.__delete_routes_in(
            self.__private_route_tables_for(source_vpc),
            source_vpc,
            destination_vpc)

    def provision(self):
        vpc_peering_connection = self.vpc_peering_relationship.fetch()

        self.__create_routes_for(self.vpc1, self.vpc2, vpc_peering_connection)
        self.__create_routes_for(self.vpc2, self.vpc1, vpc_peering_connection)

    def destroy(self):
        vpc_peering_connection = self.vpc_peering_relationship.fetch()

        self.__delete_routes_for(self.vpc1, self.vpc2, vpc_peering_connection)
        self.__delete_routes_for(self.vpc2, self.vpc1, vpc_peering_connection)

    def perform(self, action):
        getattr(self, action)()

    def _to_dict(self):
        return {
            'vpcs': frozenset([self.vpc1, self.vpc2]),
            'vpc_peering_relationship': self.vpc_peering_relationship,
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._to_dict() == other._to_dict()
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self._to_dict().items())))
