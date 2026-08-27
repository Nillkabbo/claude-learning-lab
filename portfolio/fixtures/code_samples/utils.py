import re


def slugify(text, separator="-"):
    cleaned = re.sub(r"[^a-z0-9]+", separator, text.lower())
    return cleaned.strip(separator)


def add_tag(tag, tags=[]):
    if tag not in tags:
        tags.append(tag)
    return tags


def truncate(text, limit=80):
    if len(text) <= limit:
        return text
    return text[:limit - 1] + "…"
