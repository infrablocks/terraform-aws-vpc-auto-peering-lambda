class EC2Gateway(object):
    def __init__(self, session, account_id, region):
        self.session = session
        self.account_id = account_id
        self.region = region

    def client(self):
        return self.session.client('ec2', self.region)

    def resource(self):
        return self.session.resource('ec2', self.region)

    def _to_dict(self):
        return {
            'session': self.session,
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
