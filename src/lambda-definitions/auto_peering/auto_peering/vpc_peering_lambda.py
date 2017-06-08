
def peer_vpcs_for(event, context):
    # 1. get provisioned vpc from event
    # 2. find all vpcs that depends on the vpc
    # 3. create peering connections for all combinations
    # 4. create routes for both sides in all combinations


    # log.ingo('what are we doing?')
    # log.info('looking up dependencies for: ...')
    # all_dependencies = VPCDependencies.resolve_for(event.target)
    # log.info('found dependencies')
    # for dependency in all_dependencies:
    #     log.info('establishing peering relationship')
    #     dependency.peering_relationship.perform(event.action)
    #     log.info('configuring routes')
    #     dependency.peering_routes.perform(event.action)

    return None
