import unittest
from unittest.mock import Mock

from auto_peering.tag_collection import TagCollection


class TestTagCollection(unittest.TestCase):
    def test_finds_value_by_name(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': 'ci-bronze,orders-service-silver'}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_value = tag_collection.find_value('Component')

        self.assertEqual(tag_value, 'customer-service')

    def test_returns_default_when_tags_is_none(self):
        tags = None
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_value = tag_collection.find_value('Component')

        self.assertEqual(tag_value, '')

    def test_returns_default_when_tag_not_found(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': 'ci-bronze,orders-service-silver'}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_value = tag_collection.find_value('OtherTag')

        self.assertEqual(tag_value, '')

    def test_allows_default_to_be_overridden(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': 'ci-bronze,orders-service-silver'}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        default = 'default'
        tag_value = tag_collection.find_value('OtherTag', default)

        self.assertEqual(tag_value, default)

    def test_finds_values_by_name(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': 'ci-bronze,orders-service-silver'}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_values = tag_collection.find_values('Dependencies')

        self.assertEqual(tag_values, ['ci-bronze', 'orders-service-silver'])

    def test_returns_empty_array_when_tag_does_not_exist(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': 'ci-bronze,orders-service-silver'}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_values = tag_collection.find_values('OtherThings')

        self.assertEqual(tag_values, [])

    def test_returns_empty_array_when_tag_has_empty_value(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': ''}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_values = tag_collection.find_values('Dependencies')

        self.assertEqual(tag_values, [])

    def test_returns_single_item_array_when_tag_has_single_value(self):
        tags = [
            {'Key': 'Component', 'Value': 'customer-service'},
            {'Key': 'DeploymentIdentifier', 'Value': 'gold'},
            {'Key': 'Dependencies', 'Value': 'orders-service-silver'}
        ]
        tagged = Mock()
        tagged.tags = tags

        tag_collection = TagCollection(tagged)

        tag_values = tag_collection.find_values('Dependencies')

        self.assertEqual(tag_values, ['orders-service-silver'])
