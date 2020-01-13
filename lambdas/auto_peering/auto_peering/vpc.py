from auto_peering.tag_collection import TagCollection


class VPC(object):
    def __init__(self, vpc_response, account_id, region):
        self.vpc_response = vpc_response
        self.account_id = account_id
        self.region = region
        self.tag_collection = TagCollection(self.vpc_response)

    @property
    def id(self):
        return self.vpc_response.id

    @property
    def component(self):
        return self.tag_collection.find_value('Component')

    @property
    def deployment_identifier(self):
        return self.tag_collection.find_value('DeploymentIdentifier')

    @property
    def dependencies(self):
        return self.tag_collection.find_values('Dependencies')

    @property
    def component_instance_identifier(self):
        return "{}-{}".format(self.component, self.deployment_identifier)

    @property
    def tags(self):
        return self.vpc_response.tags

    @property
    def cidr_block(self):
        return self.vpc_response.cidr_block

    def request_vpc_peering_connection(self, **kwargs):
        return self.vpc_response.request_vpc_peering_connection(**kwargs)

    def _to_dict(self):
        return {
            'vpc_response': self.vpc_response,
            'account_id': self.account_id,
            'region': self.region
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
