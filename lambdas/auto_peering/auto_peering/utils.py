def split_and_strip(comma_separated_tag_value):
    return list(filter(
        None,
        (tag_value.strip()
         for tag_value
         in comma_separated_tag_value.split(','))))
