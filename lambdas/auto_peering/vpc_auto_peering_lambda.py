import boto3
import logging
import json
import os

from auto_peering.ec2_gateways import EC2Gateways
from auto_peering.s3_event_sns_message import S3EventSNSMessage
from auto_peering.session_store import SessionStore
from auto_peering.vpc_links import VPCLinks
from auto_peering.utils import split_and_strip

logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def peer_vpcs_for(e vent, _):
    logger.info('Processing event: {}'.format(json.dumps(event)))

    default_region = os.environ.get('AWS_REGION')
    default_peering_role_name = 'vpc-auto-peering-role'

    sts_client = boto3.client('sts')
    current_account_id = sts_client.get_caller_identity()["Account"]

    search_regions = split_and_strip(
        os.environ.get('AWS_SEARCH_REGIONS') or default_region)
    search_accounts = split_and_strip(
        os.environ.get('AWS_SEARCH_ACCOUNTS') or current_account_id)
    peering_role_name = \
        os.environ.get('AWS_PEERING_ROLE_NAME') or default_peering_role_name

    session_store = SessionStore(sts_client, peering_role_name)
    ec2_gateways = EC2Gateways(session_store, search_accounts, search_regions)

    s3_event_sns_message = S3EventSNSMessage(event)
    target_account_id = s3_event_sns_message.account_id()
    target_vpc_id = s3_event_sns_message.vpc_id()
    action = s3_event_sns_message.action()
    logger.info(
        "'%s'ing peering connections for '%s'.",
        action,
        target_vpc_id)

    vpc_links = VPCLinks(ec2_gateways, logger)
    logger.info(
        "Looking up VPC links for VPC with ID: '%s'.",
        target_vpc_id)

    vpc_links_for_target = vpc_links.resolve_for(
        target_account_id, target_vpc_id)
    logger.info(
        "Found %d VPC links for VPC with ID: '%s'.",
        len(vpc_links_for_target), target_vpc_id)

    for vpc_link in vpc_links_for_target:
        logger.info(
            "Managing peering relationship between '%s' and '%s'.",
            vpc_link.vpc1.id,
            vpc_link.vpc2.id)
        vpc_link.peering_relationship.perform(action)

        logger.info(
            "Managing peering routes between '%s' and '%s'.",
            vpc_link.vpc1.id,
            vpc_link.vpc2.id)
        vpc_link.peering_routes.perform(action)
