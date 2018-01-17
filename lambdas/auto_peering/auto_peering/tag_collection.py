from auto_peering.utils import split_and_strip

class TagCollection(object):
    def __init__(self, tagged):
        self.tags = tagged.tags

    def find_value(self, key, default=''):
        if self.tags is None:
            return default

        return next(
            (tag['Value'] for tag in self.tags if tag['Key'] == key),
            default)

    def find_values(self, key):
        comma_separated_tag_value = self.find_value(key)
        tag_values = split_and_strip(comma_separated_tag_value)

        return tag_values
