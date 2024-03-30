import re


def remove_html_tags(text):
    """Remove HTML tags from a string."""
    return re.sub("<[^>]*>", "", text)
