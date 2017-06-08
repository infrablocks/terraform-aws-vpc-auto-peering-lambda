from botocore.exceptions import ClientError


class VPCPeeringRoutes(object):
    def __init__(self, vpc1, vpc2,
                 vpc_peering_relationship, ec2_client, logger):
        self.vpc1 = vpc1
        self.vpc2 = vpc2
        self.vpc_peering_relationship = vpc_peering_relationship
        self.ec2_client = ec2_client
        self.logger = logger

    def __private_route_tables_for(self, vpc):
        return self.ec2_client.route_tables.filter(
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

    def __delete_routes_in(self, route_tables, destination_vpc):
        for route_table in route_tables:
            try:
                route = self.ec2_client.Route(
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

    def __deletes_routes_for(self, source_vpc, destination_vpc,
                             vpc_peering_connection):
        self.logger.debug(
            "Removing routes from private subnets in: '%s' pointing at "
            "'%s:%s:%s'.",
            source_vpc.id, destination_vpc.id, destination_vpc.cidr_block,
            vpc_peering_connection.id)

        self.__delete_routes_in(
            self.__private_route_tables_for(source_vpc),
            destination_vpc)

    def provision(self):
        vpc_peering_connection = self.vpc_peering_relationship.fetch()

        self.__create_routes_for(self.vpc1, self.vpc2, vpc_peering_connection)
        self.__create_routes_for(self.vpc2, self.vpc1, vpc_peering_connection)

    def destroy(self):
        vpc_peering_connection = self.vpc_peering_relationship.fetch()

        self.__deletes_routes_for(self.vpc1, self.vpc2, vpc_peering_connection)
        self.__deletes_routes_for(self.vpc2, self.vpc1, vpc_peering_connection)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
