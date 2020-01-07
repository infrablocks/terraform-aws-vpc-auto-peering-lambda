from auto_peering.ec2_gateway import EC2Gateway


class EC2Gateways(object):
    def __init__(self, session_store, account_ids, regions):
        self.session_store = session_store
        self.account_ids = account_ids
        self.regions = regions

    def all(self):
        return [
            EC2Gateway(
                self.session_store.get_session_for(account_id),
                account_id,
                region)
            for account_id in self.account_ids
            for region in self.regions]

    def by_account_id_and_region(self, account_id, region):
        return EC2Gateway(
            self.session_store.get_session_for(account_id), account_id, region)

    def by_account_id(self, account_id):
        return [
            EC2Gateway(
                self.session_store.get_session_for(account_id),
                account_id,
                region)
            for region in self.regions
        ]
