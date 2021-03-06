from botocore.exceptions import ClientError


class VPCPeeringRoute(object):
    def __init__(self,
                 ec2_gateways,
                 logger,
                 between,
                 peering_relationship):
        self.vpc1 = between[0]
        self.vpc2 = between[1]
        self.vpc_peering_relationship = peering_relationship
        self.ec2_gateways = ec2_gateways
        self.logger = logger

    def __private_route_tables_for(self, vpc):
        ec2_gateway = self.ec2_gateways.\
            by_account_id_and_region(vpc.account_id, vpc.region)

        return ec2_gateway.resource().route_tables.filter(
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
                self.logger.info(
                    "Route creation succeeded for '%s'. Continuing.",
                    route_table.id)
            except ClientError as error:
                self.logger.warn(
                    "Route creation failed for '%s'. Error was: %s",
                    route_table.id, error)

    def __create_routes_for(self, source_vpc, destination_vpc,
                            vpc_peering_connection):
        self.logger.info(
            "Adding routes to private subnets in: '%s' pointing at '%s:%s:%s'.",
            source_vpc.id, destination_vpc.id, destination_vpc.cidr_block,
            vpc_peering_connection.id)

        self.__create_routes_in(
            self.__private_route_tables_for(source_vpc),
            destination_vpc, vpc_peering_connection)

    def __delete_routes_in(self, route_tables, source_vpc, destination_vpc,
                           vpc_peering_connection):
        for route_table in route_tables:
            try:
                ec2_gateway = self.ec2_gateways.\
                    by_account_id_and_region(source_vpc.account_id,
                                             source_vpc.region)
                ec2_resource = ec2_gateway.resource()
                route = ec2_resource.Route(
                    route_table.id, destination_vpc.cidr_block)
                if route.vpc_peering_connection_id == vpc_peering_connection.id:
                    route.delete()
                    self.logger.info(
                        "Route deletion succeeded for '%s'. Continuing.",
                         route_table.id)
                else:
                    self.logger.info(
                        "Route deletion skipped for '%s' as route does not "
                        "pertain to VPC peering connection '%s'. Continuing.",
                        route_table.id, vpc_peering_connection.id)
            except ClientError as error:
                self.logger.warn(
                    "Route deletion failed for '%s'. Error was: %s",
                    route_table.id, error)

    def __delete_routes_for(self, source_vpc, destination_vpc,
                            vpc_peering_connection):
        self.logger.info(
            "Removing routes from private subnets in: '%s' pointing at "
            "'%s:%s:%s'.",
            source_vpc.id, destination_vpc.id, destination_vpc.cidr_block,
            vpc_peering_connection.id)

        self.__delete_routes_in(
            self.__private_route_tables_for(source_vpc),
            source_vpc,
            destination_vpc,
            vpc_peering_connection)

    def provision(self):
        vpc_peering_connection = self.vpc_peering_relationship.fetch()

        self.__create_routes_for(self.vpc1, self.vpc2, vpc_peering_connection)

    def destroy(self):
        vpc_peering_connection = self.vpc_peering_relationship.fetch()

        self.__delete_routes_for(self.vpc1, self.vpc2, vpc_peering_connection)

    def perform(self, action):
        getattr(self, action)()

    def _to_dict(self):
        return {
            'vpcs': tuple([self.vpc1, self.vpc2]),
            'vpc_peering_relationship': self.vpc_peering_relationship,
        }

    def __repr__(self):
        return "<%s.%s object at %s: %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)),
            repr(self._to_dict()))

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
