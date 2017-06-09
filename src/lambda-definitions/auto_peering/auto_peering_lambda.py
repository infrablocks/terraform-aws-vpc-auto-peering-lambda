import boto3
import logging
import json
from auto_peering.s3_event_sns_message import S3EventSNSMessage
from auto_peering.vpc_links import VPCLinks

logging.getLogger('boto3').setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def peer_vpcs_for(event, context):
    logger.debug('Processing event: {}'.format(json.dumps(event)))
    ec2 = boto3.resource('ec2')

    s3_event_sns_message = S3EventSNSMessage(event)
    target_vpc_id = s3_event_sns_message.target()
    action = s3_event_sns_message.action()
    logger.info(
        "'%s'ing peering connections for '%s'.",
        action,
        target_vpc_id)

    vpc_links = VPCLinks(ec2, logger)
    logger.info(
        "Looking up VPC links for VPC with ID: '%s'.",
        target_vpc_id)

    vpc_links_for_target = vpc_links.resolve_for(target_vpc_id)
    logger.info(
        "Found %d VPC links for VPC with ID: '%s'.",
        len(vpc_links_for_target), target_vpc_id)

    for vpc_link in vpc_links_for_target:
        logger.info(
            "Establishing peering relationship"
            "between '%s' and '%s'.",
            vpc_link.vpc1.id,
            vpc_link.vpc2.id)
        vpc_link.peering_relationship.perform(action)

        logger.info(
            "Creating peering routes"
            "between '%s' and '%s'.",
            vpc_link.vpc1.id,
            vpc_link.vpc2.id)
        vpc_link.peering_routes.perform(action)
