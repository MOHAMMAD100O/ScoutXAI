import hashlib


def generate_hash(item):

    source = (
        item.get("source", "")
        + "|"
        + item.get("name", "")
        + "|"
        + item.get("url", "")
    )

    return hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()



def is_duplicate(item, seen_hashes):

    item_hash = generate_hash(item)

    if item_hash in seen_hashes:
        return True

    seen_hashes.add(item_hash)

    return False
