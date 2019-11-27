class EC2Gateway(object):
    def __init__(self, resource, client, region):
        self.resource = resource
        self.client = client
        self.region = region
